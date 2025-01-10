from django.urls import path
from .views import RegisterUser,ProtectedView,GenerateQRCodeZipview,DeleteurlView,QrcodeView


urlpatterns = [
    path('RegisterUser/', RegisterUser.as_view(),name='RegisterUser'),
    path('ProtectedView/', ProtectedView.as_view(),name='ProtectedView'),
    path('GenerateQRCodeZipview/', GenerateQRCodeZipview.as_view(),name='GenerateQRCodeZipview'),
    # path('DeleteurlView/', DeleteurlView.as_view(),name='DeleteurlView'),
    # path('QrcodeView/', QrcodeView.as_view(),name='QrcodeView')

]