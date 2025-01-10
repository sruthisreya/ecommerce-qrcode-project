

from rest_framework import serializers
from .models import CustomUser,UniqueURL,QRCode,Payment,ContactQuery


class UserRegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True)

    class Meta:
        model=CustomUser
        fields=['id','username','password','email','phone_no']


    def create(self,validated_data):
        user=CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            phone_no=validated_data['phone_no'],
            email=validated_data['email']
        )
        return user 
    
class UniqueurlSerializer(serializers.ModelSerializer):
    class Meta:
        model=UniqueURL
        fields='__all__'

class QRcodeSerializer(serializers.ModelSerializer):
    class Meta:
        model=QRCode
        fields='__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Payment
        fields='__all__'

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model=ContactQuery
        fields='__all__'