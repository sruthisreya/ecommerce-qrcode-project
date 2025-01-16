from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(max_length=100,unique=True)
    phn_no=models.CharField(max_length=100)
    def __str__(self):
        return self.email
    


class UniqueURL(models.Model):
    url = models.URLField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name="unique_urls")
    created_at = models.DateTimeField(auto_now_add=True)
    cost=models.DecimalField(max_digits=10,decimal_places=2)
    # qr_code_image = models.ImageField(upload_to="qr_codes/")
    def __str__(self):
        return self.url


class Details(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    closed_date = models.DateField(auto_now=True)
    unique_url = models.ForeignKey(UniqueURL, on_delete=models.CASCADE, unique=True)

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

    def calculate_total(self):
        self.total_price=sum[(url.cost*self.quantity for url in self.unique_url.all())]
        self.save()

    def __str__(self):
        return self.quantity



class Payment(models.Model):
    STATUS_CHOICES = [('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed')]
    user = models.ForeignKey(UniqueURL, on_delete=models.CASCADE)
    cart=models.ForeignKey(CartItem,on_delete=models.CASCADE)
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



