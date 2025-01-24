

from rest_framework import serializers
from .models import CustomUser,UniqueURL,Payment,ContactQuery,CartItem,Details,Images
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserRegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True)

    class Meta:
        model=CustomUser
        fields=['id','username','password','email','phn_no']


    def create(self,validated_data):
        user=CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            phn_no=validated_data['phn_no'],
            email=validated_data['email']
        )
        return user 
    

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        return {**super().validate(attrs), "message": "login successful."}


class UniqueurlSerializer(serializers.ModelSerializer):
    class Meta:
        model=UniqueURL
        fields=['id','created_at']
        # fields='__all__'



class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Payment
        fields='__all__'

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model=ContactQuery
        fields='__all__'


class CartitemSerializer(serializers.ModelSerializer):
    unique_url = UniqueurlSerializer(many=True)  

    class Meta:
        model = CartItem
        fields = ['id', 'user', 'unique_url', 'quantity', 'total_price', 'created_at']

class DetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model=Details
        fields=['unique_url','title','description','created_at']

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = ['file','detail','created_at']