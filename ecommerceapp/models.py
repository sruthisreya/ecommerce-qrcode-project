from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(max_length=100,unique=True)
    phn_no=models.CharField(max_length=100)
    def __str__(self):
        return self.email
    

class UniqueURL(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="unique_urls")
    description=models.CharField(max_length=100)
    url = models.URLField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.url



class QRCode(models.Model):
    unique_url = models.OneToOneField(UniqueURL, on_delete=models.CASCADE, related_name="qr_code")
    qr_code_image = models.ImageField(upload_to="qr_codes/")

    def __str__(self):
        return f"qr code for {self.unique_url.url}"
    

class Payment(models.Model):
    STATUS_CHOICES = [('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed')]
    user = models.ForeignKey(UniqueURL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100)
    status=models.CharField(max_length=100,choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.transaction_id}"
    


class ContactQuery(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Query from {self.email}"