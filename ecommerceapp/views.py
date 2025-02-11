
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from ecommerceapp.serializer import UserRegisterSerializer,UniqueurlSerializer,ContactSerializer,CartitemSerializer,DetailsSerializer,ImageSerializer
from rest_framework.response import Response
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
import stripe
from .permissions import IsOwnerOfUniqueUrl
from django.shortcuts import render, redirect
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .serializer import CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status

from django.db import transaction
from .models import UniqueURL,CustomUser,CartItem,Details,Payment,Images

# Create your views here.

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

class RegisterUser(APIView):
    permission_classes=[AllowAny]

    def post(self,request):
        serializer=UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message":" Registration was Successfull",
                    "user":serializer.data
                },status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProtectedView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]

    def get(self,request):
        return Response({"message":"you are authenticated"})
    
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


def create_50_urls(request):
    print("hello")
    for i in range(50):
        UniqueURL.objects.create()
    return HttpResponseRedirect("../")


#to view all urls
class UniqueurlView(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]

    def get(self,request):
        user=request.user
        user_urls=UniqueURL.objects.all()
        serializer = UniqueurlSerializer(user_urls, many=True)
        return Response(serializer.data)
    

# add urls to cart
class AddurlsTocartView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        user = request.user
        quantity = request.data.get('quantity')
        if not isinstance(quantity, int) or quantity <= 0:
            return Response({"detail": "Quantity must be a positive integer."}, status=status.HTTP_400_BAD_REQUEST)
        
        unique_urls = UniqueURL.objects.filter(in_cart=False, user__isnull=True)[:quantity]
        if len(unique_urls) < quantity:
            return Response({"detail": "Not enough URLs to purchase"}, status=status.HTTP_404_NOT_FOUND)
        
        total_price = sum(url.cost for url in unique_urls) 
        with transaction.atomic():
            cart_item, created = CartItem.objects.get_or_create(user=user, is_closed=False, defaults={"quantity": 0, "total_price": 0} )
            cart_item.quantity += quantity
            cart_item.total_price += total_price
            cart_item.save()
            cart_item.unique_url.add(*unique_urls)
            UniqueURL.objects.filter(id__in=[url.id for url in unique_urls]).update(in_cart=True)
        serialized_urls = UniqueurlSerializer(cart_item.unique_url.all(), many=True).data
        
        return Response({
            "message": "URLs added to cart successfully!",
            "cart_id": cart_item.id,
            "total_price": cart_item.total_price,
            "quantity": cart_item.quantity,
            "added_urls": serialized_urls
        }, status=status.HTTP_201_CREATED)


class DeleteurlView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def delete(self, request):
        user = request.user
        quantity = request.data.get('quantity')
        if not isinstance(quantity, int) or quantity <= 0:
            return Response({"detail": "Quantity must be a positive integer."}, status=status.HTTP_400_BAD_REQUEST)
        
        cart_item = CartItem.objects.filter(user=user, is_closed=False).first()
        if not cart_item:
            return Response({"detail": "No open cart found for this user."}, status=status.HTTP_404_NOT_FOUND)
        
        current_quantity = cart_item.unique_url.count()
        if current_quantity < quantity:
            return Response({"detail": f"Not enough URLs in cart. Cart has only {current_quantity} URLs."}, status=status.HTTP_400_BAD_REQUEST)
        
        urls_to_delete = cart_item.unique_url.all()[:quantity]
        with transaction.atomic():
            cart_item.unique_url.filter(id__in=[url.id for url in urls_to_delete]).delete()
            UniqueURL.objects.filter(id__in=[url.id for url in urls_to_delete]).update(in_cart=False)
            total_price_decreased = sum(url.cost for url in urls_to_delete)
            cart_item.total_price -= total_price_decreased
            cart_item.quantity -= len(urls_to_delete) #quantity
            cart_item.save()
        
        serialized_urls = UniqueurlSerializer(cart_item.unique_url.all(), many=True).data
        return Response({
            "message": "URLs removed from cart successfully!",
            "cart_id": cart_item.id,
            "total_price": cart_item.total_price,
            "quantity": cart_item.quantity,
            "remaining_urls": serialized_urls
        }, status=status.HTTP_200_OK)


#remaining urls
class OpencartView(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]

    def get(self,request):
        user=request.user
        quantity = request.query_params.get('quantity')
        cart_items=CartItem.objects.filter(user=user, is_closed=False)
        # serializer=CartitemSerializer(cart_item,many=True)
        remaining_urls=[]
        total_price=0
        for cart_item in cart_items:
            urls = cart_item.unique_url.all()
        if quantity:
            try:
                 quantity = int(quantity)  
            except ValueError:
                return Response({"detail": "Invalid quantity value."}, status=status.HTTP_400_BAD_REQUEST)
            urls = urls[:quantity]
        remaining_urls.extend(urls) 
        total_price += sum(url.cost for url in urls)
        
        serialized_urls = UniqueurlSerializer(remaining_urls, many=True)
        return Response({
            "cart_id":cart_item.id,
            "quantity": len(remaining_urls),
            "remaining_urls": serialized_urls.data,
            "total_price": total_price
        }, status=status.HTTP_200_OK)
    

class DetailsView(APIView):
    permission_classes=[IsAuthenticated, IsOwnerOfUniqueUrl]
    authentication_classes=[JWTAuthentication]

    def put(self, request, url_id):
        unique_url = get_object_or_404(UniqueURL, id=url_id)
        details_instance, _ = Details.objects.get_or_create(unique_url=unique_url)
        self.check_object_permissions(request, unique_url)
        serializer = DetailsSerializer(details_instance, data=request.data, context={'request': request}, partial=True)  
        
        if serializer.is_valid():
            details_instance = serializer.save()
            return Response(DetailsSerializer(details_instance).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class DetailsgetView(APIView):
    permission_classes=[AllowAny]

    def get(self, request, url_id):
        unique_url = get_object_or_404(UniqueURL, id=url_id)
        details = get_object_or_404(Details, unique_url=unique_url)
        serializer = DetailsSerializer(details)
        return Response(serializer.data, status=status.HTTP_200_OK) 


#payment
class Paymentcreateview(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        cart_id = request.data.get("cart_id")
        if not cart_id:
            return Response({"error": "Cart ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            cart = CartItem.objects.get(id=cart_id, user=request.user, is_closed=False)
            total_amount = int(cart.total_price * 100)
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "inr",
                        "product_data": {"name": f"Purchase Unique URL - {cart.id}"},
                        "unit_amount": total_amount,
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url=f"{settings.YOUR_DOMAIN}/api/v1/payment-success/?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.YOUR_DOMAIN}/api/v1/payment-cancel",
            )
            unique_url = cart.unique_url.first()
            
            if not unique_url:
                return Response({"error": "No UniqueURL linked to this cart."}, status=status.HTTP_400_BAD_REQUEST)
            
            user = unique_url.user if unique_url.user else cart.user
            if not user:
                return Response({"error": "No associated user found for this cart."}, status=status.HTTP_400_BAD_REQUEST)
            
            payment = Payment.objects.create(
                cart=cart,
                user=user,
                total_amount=total_amount,
                status="PENDING",
                checkout_id=session.id,
            )
            
            return Response({
                "message": "Stripe Checkout session created successfully.",
                "session_id": session.id,
                "url": session.url,
                "payment_id": payment.id,
            }, status=status.HTTP_201_CREATED)
        except CartItem.DoesNotExist:
            return Response({"error": "Cart not found or unauthorized access."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class PaymentSuccessView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        session_id = request.GET.get('session_id')
        if not session_id:
            return Response({"error": "Session ID not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            payment = Payment.objects.get(checkout_id=session_id)
            if session.payment_status == "paid":
                payment.status = "COMPLETED"
                print(payment.status)
                payment.transaction_id = session.payment_intent 
                payment.save()
                cart = payment.cart
                if cart and not cart.is_closed:
                    cart.is_closed = True
                    cart.save()
                for unique_url in cart.unique_url.all():
                    unique_url.user=cart.user
                    unique_url.save()

                #for i in cart user field update 
                # notify user
                user_email = payment.cart.user.email if payment.cart and payment.cart.user else None
                if user_email:
                    send_mail(
                        subject="Payment ",
                        message=(
                            f"Dear {payment.cart.user.username},\n\n"
                            f"Thank you for your payment.\n"
                            f"title: URL purchased.\n"
                            f"Payment ID: {payment.id}\n"
                            f"Total Amount: ${payment.total_amount / 100}\n"
                            f"Status: Completed\n\n"
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user_email]
                    )
                # Notify admin
                admin_email = settings.DEFAULT_FROM_EMAIL
                send_mail(
                    subject="New Payment Notification",
                    message=(
                        f"A new payment has been completed.\n\n"
                        f"Payment Details:\n"
                        f"Payment ID: {payment.id}\n"
                        f"User: {payment.user}\n"
                        f"Total Amount: ${payment.total_amount / 100}\n"
                        f"Status: Completed\n\n"
                    ),
                    from_email=admin_email,
                    recipient_list=[admin_email]
                )
                context = {
                'payment': payment,
                'payment_id': payment.id,
                'transaction_id': payment.transaction_id,
                "total_amount":payment.total_amount / 100,
                'user': payment.user,
            }
                return render(request, 'success.html', context)
                # return redirect(f"/success/{payment.id}/")
                # return Response({
                #     "message": "Payment successful.",
                #     "payment_id": payment.id,
                #     "transaction_id": payment.transaction_id,  
                #     "total_amount": payment.total_amount / 100,
                #     "payment_status": session.payment_status,
                # })
            else:
                return Response({"error": "Payment was not successful"}, status=status.HTTP_400_BAD_REQUEST)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentCancelView(APIView):

    def get(self, request):
        session_id = request.GET.get('session_id')   
        
        if not session_id:
            return JsonResponse({"error": "Session ID not provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            payment = Payment.objects.get(transaction_id=session_id)
            payment.status = "FAILED" 
            payment.save()
            context = {
                'payment': payment,
                'payment_id': payment.id,
                'status': payment.status,
                'user': payment.user,
            }
            
            return render(request, 'cancel.html', context)
            # return redirect(f"/cancel/{payment.id}/")
            # return JsonResponse({
            #     "message": "Your payment was cancelled. Please try again if you wish to complete the payment.",
            #     "payment_id": payment.id,
            #     "status": payment.status,
            # })
        except Payment.DoesNotExist:
            return JsonResponse({"error": "Payment not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


  #feedback  
class ContactQueryView(APIView):
    permission_classes=[AllowAny]

    def post(self,request):
        serializer = ContactSerializer(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message":"your feedback has been submitted successfully"}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



