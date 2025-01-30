

from rest_framework import serializers
from .models import CustomUser,UniqueURL,Payment,ContactQuery,CartItem,Details,Images
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import re
from django.core.exceptions import ValidationError


class UserRegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True)

    class Meta:
        model=CustomUser
        fields=['id','username','password','email','phone_no']

    def validate_email(self, value):
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, value):
            raise ValidationError("Enter a valid email address.")
        return value


    def validate_phn_no(self, value):
        if not re.match(r'^\d{10}$', value):
            raise ValidationError("Phone number must be 10 digits.")
        if CustomUser.objects.filter(phone_no=value).exists():
            raise ValidationError("A user with this phone number already exists.")
        return value
    
    
    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise ValidationError("A user with this username already exists.")
        return value


    def create(self,validated_data):
        user=CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            phone_no=validated_data['phone_no'],
            email=validated_data['email']
        )
        return user 
    

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        return {**super().validate(attrs), "message": "login successful."}
    

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = ['file','detail','created_at']

class DetailsSerializer(serializers.ModelSerializer):
    images=ImageSerializer(many=True,read_only=True)
    class Meta:
        model=Details
        fields=['unique_url','title','description','images']



class UniqueurlSerializer(serializers.ModelSerializer):
    # details=DetailsSerializer()
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




# class DetailsUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Details
#         fields = ['title', 'description']


