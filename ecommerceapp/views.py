
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from ecommerceapp.serializer import UserRegisterSerializer,UniqueurlSerializer,ContactSerializer,CartitemSerializer,DetailsSerializer
from rest_framework.response import Response
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.conf import settings
from django.shortcuts import get_object_or_404
from .serializer import CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from .models import UniqueURL,CustomUser,CartItem,Details

# Create your views here.

# stripe.api_key = settings.STRIPE_SECRET_KEY

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

#delete urls
class DeleteurlView(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]

    def delete(self,request,url_id):
        user=request.user
        cartitm=CartItem.objects.filter(user=user,is_closed=False).first()
        if not cartitm:
            return Response({"detail": "No open cart found."}, status=status.HTTP_404_NOT_FOUND)
        unique_url = get_object_or_404(UniqueURL, id=url_id)
        if unique_url not in cartitm.unique_url.all():
            return Response({"detail": "URL not found in cart."}, status=status.HTTP_404_NOT)
        cartitm.unique_url.remove(unique_url)
        # cartitm.save()
        return Response({"message": "URL removed from cart successfully"}, status=status.HTTP_200_OK)
    

class OpencartView(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]

    def get(self,request):
        user=request.user
        cart_item=CartItem.objects.filter(user=user,is_closed=False).first()
        if not cart_item:
            return Response({"detail": "No open cart found."}, status=status.HTTP_404_NOT_FOUND)
        remaining_urls=cart_item.unique_url.all()
        updated_quantity = remaining_urls.count()
        updated_total_price = sum(url.cost for url in remaining_urls)
        cart_item.quantity = updated_quantity
        cart_item.total_price = updated_total_price
        cart_item.save()
        serializedurls=UniqueurlSerializer(remaining_urls,many=True)
        return Response({
            "cart_id": cart_item.id,
            "total_price": cart_item.total_price,
            "quantity": cart_item.quantity,
            "remaining_urls": serializedurls.data
        }, status=status.HTTP_200_OK)

    
  #feedback  
class ContactQueryView(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]

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

#payment
class Paymentcreateview(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    def post(self,request):
        serializer=DetailsSerializer(data=request.data)
        if serializer.is_valid():
            payment=serializer.save()
            return Response({"message": f"Payment {payment.transaction_id} created successfully!", "payment_id": payment.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
#add urls to cart
class AddurlsTocartView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        user = request.user
        url_ids = request.data.get('url_ids', []) 
        if not url_ids:
            return Response({"detail": "No URL IDs provided."}, status=status.HTTP_400_BAD_REQUEST)
        from uuid import UUID
        try:
            url_ids = [UUID(id_str) for id_str in url_ids]
        except ValueError:
            return Response({"detail": "Invalid URL ID format."}, status=status.HTTP_400_BAD_REQUEST)
        unique_urls = UniqueURL.objects.filter(id__in=url_ids)
        if not unique_urls.exists():
            return Response({"detail": "No URLs found for the provided IDs."}, status=status.HTTP_404_NOT_FOUND)
        total_price = sum(url.cost for url in unique_urls)
        cart_item = CartItem.objects.create(user=user, quantity=len(unique_urls), total_price=total_price)
        cart_item.unique_url.set(unique_urls)
        cart_item.save()
        send_mail(
            subject="URLs added to the cart",
            message=(
                f"Dear {user.username} You have successfully added {len(unique_urls)} URLs to your cart"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
        send_mail(
            subject="Urls added to the cart",
            message=(
                f"User {user.username} has added {len(unique_urls)} URLs to the cart"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['sreyamaya84@gmail.com'],
        )
        return Response({
            "message": "URLs added to cart successfully!",
            "cart_id": cart_item.id,
            "total_price": cart_item.total_price,
            "quantity": cart_item.quantity
        }, status=status.HTTP_201_CREATED)
    

class DetailsView(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    def post(self,request,url_id):
        unique_url = UniqueURL.objects.get(id=url_id)
        data=request.data
        data['unique_url']=unique_url.id
        serializer=DetailsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self,request,url_id):
        detail=Details.objects.all()
        serializer=DetailsSerializer(detail)
        return Response(serializer.data)
    
    def put(self, request, url_id):
        try:
            unique_url = UniqueURL.objects.get(id=url_id)
            details = Details.objects.get(unique_url=unique_url)
        except (UniqueURL.DoesNotExist, Details.DoesNotExist):
            return Response({"detail": "Details or Unique URL not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = DetailsSerializer(details, data=request.data, partial=True) 
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
