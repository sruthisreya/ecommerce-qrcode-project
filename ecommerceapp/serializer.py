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
        fields = ['file']

class DetailsSerializer(serializers.ModelSerializer):
    images=ImageSerializer(many=True, read_only=True)
    unique_url = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model=Details
        fields=['unique_url','title','description','images']

    def create(self, validated_data):

            # Extract title and description from validated data
        title = validated_data.get('title', "")
        description = validated_data.get('description', "")
        details_instance = Details.objects.create(
            unique_url=validated_data['unique_url'],
            title=title,
            description=description
        )
        image_data = self.context['request'].FILES.getlist('file')
        for image in image_data:
            Images.objects.create(detail=details_instance, file=image)
        return details_instance
    def update(self, instance, validated_data):

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        image_data = self.context['request'].FILES.getlist('file')
        if image_data:
            Images.objects.filter(detail=instance).delete()
            for image in image_data:
                Images.objects.create(detail=instance, file=image)
        return instance
 

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




