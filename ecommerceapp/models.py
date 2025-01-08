from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(max_length=100,unique=True)
    phn_no=models.CharField(max_length=100)
    def __str__(self):
        return self.email
    

class UniqueURL(models.Model):
    url = models.URLField(unique=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.url


