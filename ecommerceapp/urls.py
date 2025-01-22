from django.urls import path
from .views import RegisterUser,ProtectedView,ContactQueryView,UniqueurlView,AddurlsTocartView,DeleteurlView, create_50_urls,Paymentcreateview,OpencartView,CustomTokenObtainPairView,DetailsView

from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

app_name = 'package'

urlpatterns = [
    path('RegisterUser/', RegisterUser.as_view(),name='RegisterUser'),
    path('ProtectedView/', ProtectedView.as_view(),name='ProtectedView'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token-btain-pair'),
    # path('token/',TokenObtainPairView.as_view(),name='token'),
    path('refresh/',TokenRefreshView.as_view(),name='refresh'),
    path('create-url/', create_50_urls, name='create-url'),
    path('UniqueurlView/',UniqueurlView.as_view(),name='UniqueurlView'),
    path('OpencartView/',OpencartView.as_view(),name='OpencartView'),
    path('ContactQueryView/',ContactQueryView.as_view(),name='ContactQueryView'),
    path('AddurlsTocartView/',AddurlsTocartView.as_view(),name='AddurlsTocartView'),
    path('DeleteurlView/<str:url_id>',DeleteurlView.as_view(),name='DeleteurlView'),
    path('Paymentcreateview',Paymentcreateview.as_view(),name='Paymentcreateview'),
    path('url/<str:url_id>/details',DetailsView.as_view(),name='DetailsView'),
    path('url/<str:url_id>/update',DetailsView.as_view(),name='DetailsView'),

    
    # path('UniqueurlmanagementView/',UniqueurlmanagementView.as_view(),name='UniqueurlmanagementView'),
]