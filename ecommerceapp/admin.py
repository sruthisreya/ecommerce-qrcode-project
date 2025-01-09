from django.contrib import admin
from .models import CustomUser,UniqueURL,QRCode,Payment,ContactQuery

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(UniqueURL)
admin.site.register(QRCode)
admin.site.register(Payment)
admin.site.register(ContactQuery)
