from django.urls import path
from .views import RegisterUser,ProtectedView,download_qr_codes,ContactQueryView,UniqueurlView,AddurlsTocartView,DeleteurlView
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

urlpatterns = [
    path('RegisterUser/', RegisterUser.as_view(),name='RegisterUser'),
    path('ProtectedView/', ProtectedView.as_view(),name='ProtectedView'),
    path('token/',TokenObtainPairView.as_view(),name='token'),
    path('refresh/',TokenRefreshView.as_view(),name='refresh'),
    path('download-qr-codes/', download_qr_codes, name='download_qr_codes'),
    path('UniqueurlView/',UniqueurlView.as_view(),name='UniqueurlView'),
    path('ContactQueryView/',ContactQueryView.as_view(),name='ContactQueryView'),
    path('AddurlsTocartView/<int:url_id>',AddurlsTocartView.as_view(),name='AddurlsTocartView'),
    path('DeleteurlView/<int:url_id>',DeleteurlView.as_view(),name='DeleteurlView'),
    
    # path('UniqueurlmanagementView/',UniqueurlmanagementView.as_view(),name='UniqueurlmanagementView'),
]