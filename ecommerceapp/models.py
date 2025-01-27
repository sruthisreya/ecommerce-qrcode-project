import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    email = models.EmailField(max_length=100, unique=True)
    phn_no=models.CharField(max_length=100)

    def __str__(self):
        return self.email
    

class UniqueURL(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, blank=True, null=True, on_delete=models.SET_NULL, related_name="unique_url_user")
    in_cart = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    cost=models.DecimalField(max_digits=10,decimal_places=2)

    def save(self,*args,**kwargs):
        if self.cost is None or self.cost==0.0:
            self.cost=100
        super().save(*args,**kwargs)

    def __str__(self):
        return str(self.id)


class Details(models.Model):
    unique_url = models.OneToOneField(UniqueURL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    closed_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.title


class Images(models.Model):
    file=models.FileField(upload_to='uploads/')
    created_at=models.DateTimeField(auto_now=True)
    detail=models.ForeignKey(Details,on_delete=models.CASCADE)
    def __str__(self):
        return self.file.name


class CartItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    unique_url = models.ManyToManyField(UniqueURL)
    is_closed = models.BooleanField(default=False)
    quantity = models.PositiveIntegerField(default=1)
    total_price=models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.user.email} with {self.quantity} items"


class Payment(models.Model):
    STATUS_CHOICES = [('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed')]
    user = models.ForeignKey(UniqueURL, on_delete=models.CASCADE)
    cart=models.ForeignKey(CartItem,on_delete=models.CASCADE)
    checkout_id = models.CharField(max_length=100)
    transaction_id = models.CharField(max_length=100)
    status=models.CharField(max_length=100,choices=STATUS_CHOICES)
    total_amount=models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.transaction_id}"
    

class ContactQuery(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Query from {self.email}"
