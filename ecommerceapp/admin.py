from django.contrib import admin
from .models import CustomUser,UniqueURL,QRCode,Payment,ContactQuery

# Register your models here.
class Useradmin(admin.ModelAdmin):
    list_display=['username','email','phn_no']
admin.site.register(CustomUser,Useradmin)


class UniqueurlAdmin(admin.ModelAdmin):
    list_display=['description','url','created_at']
admin.site.register(UniqueURL,UniqueurlAdmin)


class QrCodeAdmin(admin.ModelAdmin):
    list_display=['unique_url','qr_code_image']
admin.site.register(QRCode, QrCodeAdmin)


class PaymentAdmin(admin.ModelAdmin):
    list_display=['user','amount','transaction_id','status','created_at']
admin.site.register(Payment, PaymentAdmin)


class ContactQueryAdmin(admin.ModelAdmin):
    list_display=['name','email','message','created_at']
admin.site.register(ContactQuery,ContactQueryAdmin)


