

from rest_framework import serializers
from .models import CustomUser,UniqueURL,Payment,ContactQuery,CartItem,Details


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
    
class UniqueurlSerializer(serializers.ModelSerializer):
    class Meta:
        model=UniqueURL
        fields=['id','url','created_at']



class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Payment
        fields='__all__'

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model=ContactQuery
        fields='__all__'


class CartitemSerializer(serializers.ModelSerializer):
    # url_id=UniqueurlSerializer(many=True)
    class Meta:
        model=CartItem
        fields=['id','user','unique_url','quantity','created_at']


class DetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model=Details
        fields='__all__'