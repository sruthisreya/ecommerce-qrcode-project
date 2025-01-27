
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
from django.shortcuts import get_object_or_404
from .serializer import CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status

from django.db import transaction
from .models import UniqueURL,CustomUser,CartItem,Details,Payment

# Create your views here.

# stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

class RegisterUser(APIView):
    permission_classes=[AllowAny]

    def post(self,request):
        serializer=UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProtectedView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]

    def get(self,request):
        return Response({"message":"you are authenticated"})
    
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

#to view all urls
class UniqueurlView(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]

    def get(self,request):
        user=request.user
        user_urls=UniqueURL.objects.all()
        serializer = UniqueurlSerializer(user_urls, many=True)
        return Response(serializer.data)
    


#add urls to cart
class AddurlsTocartView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        user = request.user
        quantity = request.data.get('quantity')
        try:
            quantity = int(quantity)
            if quantity <= 0:
                return Response({"detail": "Quantity must be greater than zero."}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError):
            return Response({"detail": "Invalid quantity provided."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            unique_urls = UniqueURL.objects.filter(in_cart=False, user__isnull=True)[:quantity]
        except:
            return Response({"message": "Not enough unique URLs"}, status=status.HTTP_400_BAD_REQUEST) 
        if not unique_urls.exists() or len(unique_urls) < quantity:
            return Response({"detail": "Not enough URLs to purchase"}, status=status.HTTP_404_NOT_FOUND)
        total_price = sum(url.cost for url in unique_urls)

        with transaction.atomic():
            cart_item = CartItem.objects.create(user=user, quantity=quantity, total_price=total_price)
            cart_item.unique_url.set(unique_urls)
            UniqueURL.objects.filter(id__in=[url.id for url in unique_urls]).update(in_cart=True)
        serialized_urls = UniqueurlSerializer(unique_urls, many=True).data
        send_mail(
            subject="URLs added to the cart",
            message=f"Dear {user.username}, You have successfully added {len(unique_urls)} URLs to your cart",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
        send_mail(
            subject="Urls added to the cart",
            message=f"User {user.username} has added {len(unique_urls)} URLs to the cart",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['sreyamaya84@gmail.com'],
        )
        return Response({
            "message": "URLs added to cart successfully!",
            "cart_id": cart_item.id,
            "total_price": cart_item.total_price,
            "quantity": cart_item.quantity,
            "added_urls": serialized_urls  
        }, status=status.HTTP_201_CREATED) 



  #feedback  
class ContactQueryView(APIView):
    permission_classes=[AllowAny]

    def post(self,request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message":"your feedback has been submitted successfully"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


def create_50_urls(request):
    for i in range(50):
        UniqueURL.objects.create()
    return HttpResponseRedirect("../../")
    


class DeleteurlView(APIView):   #2nd code for delete
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def delete(self, request):
        user = request.user
        quantity = request.data.get('quantity') 
        if not quantity or quantity <= 0:
            return Response({"detail": "Please provide a valid quantity"}, status=status.HTTP_400_BAD_REQUEST)  
        cart_items = CartItem.objects.filter(user=user, is_closed=False).order_by('-created_at')
        if not cart_items.exists():
            return Response({"detail": "No open cart found"}, status=status.HTTP_404_NOT_FOUND)
        with transaction.atomic():
            removed_urls = []
            total_amount = 0
            for cart_item in cart_items:
                urls_to_remove = cart_item.unique_url.all()[:quantity]
                if not urls_to_remove:
                    continue
                total_amount = sum(url.cost for url in urls_to_remove)
                amount = total_amount
                cart_item.unique_url.remove(*urls_to_remove)
                cart_item.quantity -= len(urls_to_remove)
                amount += len(urls_to_remove)
                removed_urls.extend(urls_to_remove)
                UniqueURL.objects.filter(id__in=[url.id for url in urls_to_remove]).update(in_cart=False)
                if cart_item.quantity == 0:
                    cart_item.delete()
                else:
                    cart_item.save()
                if len(removed_urls) >= quantity:
                    break  
            if total_amount == 0:
                return Response({"detail": "No URLs found to remove"}, status=status.HTTP_404_NOT_FOUND)
            remaining_cart_total = sum(
                sum(url.cost for url in cart_item.unique_url.all()) 
                for cart_item in cart_items
            ) 
            serialized_removed_urls = UniqueurlSerializer(removed_urls, many=True).data
        return Response({
            "message": "URLs removed from cart successfully!",
            "removed_quantity": len(removed_urls),
            "Amount": total_amount,
            "remaining_total_cost": remaining_cart_total,
            "removed_urls": serialized_removed_urls
        }, status=status.HTTP_200_OK)



#remaining urls
class OpencartView(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]

    def get(self,request):
        user=request.user
        quantity = request.query_params.get('quantity')
        cart_items=CartItem.objects.filter(user=user,is_closed=False)
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
            "quantity": len(remaining_urls),
            "remaining_urls": serialized_urls.data,
            "total_price": total_price
        }, status=status.HTTP_200_OK)
    

class ImageUploadView(APIView):
    parser_classes=(MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer=ImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Image uploaded successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class DetailsView(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    def get(self, request, url_id, *args, **kwargs):
        unique_url = get_object_or_404(UniqueURL, id=url_id)
        details = get_object_or_404(Details, unique_url=unique_url)
        serializer = DetailsSerializer(details)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, url_id, *args, **kwargs):
        unique_url = get_object_or_404(UniqueURL, id=url_id)
        details = get_object_or_404(Details, unique_url=unique_url)

        serializer = DetailsSerializer(details, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Details updated successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



#payment
class Paymentcreateview(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    def post(self,request):
        cart_id = request.data.get("cart_id")
        if not cart_id:
            return Response({"error": "Cart ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            cart = CartItem.objects.get(id=cart_id, user=request.user, is_closed=False)
            total_amount = 0
            for url in cart.unique_url.all():
                total_amount += int(url.cost * cart.quantity)
                session = stripe.checkout.Session.create(
                    payment_method_types=["card"],
                    line_items=[{
                        "price_data": {
                        "currency": "usd",
                        "product_data": {"name": f"Purchase Unique URL - {url.name}"},  
                        "unit_amount": int(url.cost * 100),  
                    },
                    "quantity": cart.quantity,
                } for url in cart.unique_url.all()],
                mode="payment",
                success_url=f"{settings.YOUR_DOMAIN}/payment-success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.YOUR_DOMAIN}/payment-cancel",
            )
                payment = Payment.objects.create(
                cart=cart,
                total_amount=total_amount,
                status="pending",
                transaction_id=session.id,
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
