
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from ecommerceapp.serializer import UserRegisterSerializer,UniqueurlSerializer
from rest_framework.response import Response
from django.http import HttpResponse
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import status
from .models import UniqueURL,QRCode
import zipfile
import qrcode
from io import BytesIO

# Create your views here.


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
    


class GenerateQRCodeZipview(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        urls = request.data.get('urls') 
        if not urls or not isinstance(urls, list):
            return Response({'error': 'A list of URLs is required'}, status=400)
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for index, url in enumerate(urls):   
                unique_url, created = UniqueURL.objects.get_or_create(user=user, url=url)
                if not hasattr(unique_url, 'qr_code'):
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(url)
                    qr.make(fit=True)
                    qr_image = BytesIO()
                    qr_img = qr.make_image(fill_color="black", back_color="white")
                    qr_img.save(qr_image, format='PNG')
                    qr_image.seek(0)
                    QRCode.objects.create(
                        unique_url=unique_url,
                        qr_code_image=InMemoryUploadedFile(
                            qr_image,
                            None,
                            f"qr_{unique_url.id}.png",
                            'image/png',
                            qr_image.getbuffer().nbytes,
                            None
                        )
                    )
                qr_image = unique_url.qr_code.qr_code_image
                zip_file.write(qr_image.path, f"qr_code_{index + 1}.png")
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="qr_codes.zip"'
        return response
    


class QrcodeView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        uniqueurl=UniqueURL.objects.filter(user=request.user)
        serializer=UniqueurlSerializer(uniqueurl,many=True)
        return Response(serializer.data)


class DeleteurlView(APIView):
    permission_classes=[IsAuthenticated]
    def delete(self,request,url_id):
        try:
            unique_url=UniqueURL.objects.get(id=url_id,user=request.user)
        except UniqueURL.DoesNotExist:
            return Response({"error":"url not found"},status=status.HTTP_404_NOT_FOUND)
        unique_url.delete()
        return Response({"success":"url deleted"},status=status.HTTP_200_OK)
    

    
    
    
        




        
