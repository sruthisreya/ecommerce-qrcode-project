from django.urls import path
from .views import RegisterUser,ProtectedView,ContactQueryView,UniqueurlView,AddurlsTocartView,DeleteurlView,create_50_urls,Paymentcreateview,OpencartView,CustomTokenObtainPairView,DetailsView,PaymentCancelView,PaymentSuccessView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView


app_name = 'package'


urlpatterns = [
    path('RegisterUser/', RegisterUser.as_view(),name='RegisterUser'),
    path('ProtectedView/', ProtectedView.as_view(),name='ProtectedView'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token-btain-pair'),
    # path('token/',TokenObtainPairView.as_view(),name='token'),
    path('refresh/',TokenRefreshView.as_view(),name='refresh'),
    path('create-url/', create_50_urls, name='create-url'),
    path('UniqueurlView/',UniqueurlView.as_view(),name='UniqueurlView'),
    path('OpencartView/',OpencartView.as_view(),name='OpencartView'),
    path('ContactQueryView/',ContactQueryView.as_view(),name='ContactQueryView'),
    path('AddurlsTocartView/',AddurlsTocartView.as_view(),name='AddurlsTocartView'),
    path('DeleteurlView/',DeleteurlView.as_view(),name='DeleteurlView'),
    path('Paymentcreateview/',Paymentcreateview.as_view(),name='Paymentcreateview'),
    path('payment-success/',PaymentSuccessView.as_view(),name='paymentsuccess'),
    path('payment/cancel/',PaymentCancelView.as_view(),name='paymentcancel'),
    # path('url/<str:url_id>/upload-image/',ImageUploadView.as_view(),name='upload-image'),
   
    path('url/<str:url_id>/details',DetailsView.as_view(),name='DetailsView'),
    path('url/<str:url_id>/update',DetailsView.as_view(),name='DetailsView'),

    # path('UniqueurlmanagementView/',UniqueurlmanagementView.as_view(),name='UniqueurlmanagementView'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
