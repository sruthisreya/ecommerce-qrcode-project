
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from ecommerceapp.serializer import UserRegisterSerializer,UniqueurlSerializer,ContactSerializer,CartitemSerializer
from rest_framework.response import Response
from django.http import HttpResponse
from django.shortcuts import get_list_or_404,get_object_or_404
import qrcode
import io 
import zipfile
from rest_framework import status
from .models import UniqueURL,CustomUser,CartItem


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
    


def download_qr_codes(request):
    ids = request.GET.get('ids', '')
    ids = ids.split(',')
    queryset = get_list_or_404(CustomUser, id__in=ids)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as zip_file:
        for obj in queryset:
            qr = qrcode.make(f"ID: {obj.id}, UserName: {obj.username}")
            qr_io = io.BytesIO()
            qr.save(qr_io, format='PNG')
            qr_io.seek(0)
            zip_file.writestr(f"{obj.username}_QRCode.png", qr_io.read())
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="qr_codes.zip"'
    return response



class UniqueurlView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        user=request.user
        user_urls = UniqueURL.objects.filter(user=user)
        serializer = UniqueurlSerializer(user_urls, many=True)
        return Response(serializer.data)


class AddurlsTocartView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        user=request,user
        unique_urls=UniqueURL.objects.filter(user=user)
        if not unique_urls.exists():
            return Response({"detail": "No URLs found for this user."}, status=status.HTTP_404_NOT_FOUND)
        cart_item = CartItem.objects.create(user=user, quantity=len(unique_urls))
        cart_item.unique_url.set(unique_urls)
        cart_item.save()
        return Response({
            "message": "URLs added to cart successfully",
            "cart_item": CartitemSerializer(cart_item).data
        }, status=status.HTTP_201_CREATED)
    def get(self,request):
        user=request.user
        cartitm=CartItem.objects.filter(user=user,is_closed=False)
        if not cartitm.exists():
            return Response({'message':'no active cart item found'},status=status.HTTP_404_NOT_FOUND)
        serializer=CartitemSerializer(cartitm,many=True)
        return Response(serializer.data)    

class DeleteurlView(APIView):
    permission_classes=[IsAuthenticated]
    def delete(self,request,url_id):
        user=request.user
        cartitm=CartItem.objects.filter(user=user,is_closed=False).first()
        if not cartitm:
            return Response({"detail": "No open cart found."}, status=status.HTTP_404_NOT_FOUND)
        unique_url = get_object_or_404(UniqueURL, id=url_id)
        if unique_url not in cartitm.unique_url.all():
            return Response({"detail": "URL not found in cart."}, status=status.HTTP_404_NOT)
        cartitm.unique_url.remove(unique_url)
        cartitm.save()
        return Response({"message": "URL removed from cart successfully"}, status=status.HTTP_200_OK)
    



    
class ContactQueryView(APIView):
    def post(self,request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message":"your feedback has been submitted successfully"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


    
    
    
        




        
