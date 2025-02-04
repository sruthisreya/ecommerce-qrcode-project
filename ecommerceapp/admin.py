from django.contrib import admin
from django.http import HttpResponseRedirect,HttpResponse
# from django.urls import reverse
import string
import io
import zipfile
from django.urls import path
import qrcode
from django.contrib import messages
import random
# from admin_extra_buttons import api
# from admin_extra_buttons.api import button
from .models import CustomUser,UniqueURL,Payment,ContactQuery,CartItem,Details,Images


# Register your models here.
@admin.action(description="generate qr codes")
def generate_qr_codes(modeladmin, request, queryset):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as zip_file:
        for obj in queryset:
            qr = qrcode.make(f"http://localhost:8000/api/vi/url/{obj.id}/details")
            qr_io = io.BytesIO()   #memory file operatn handle
            qr.save(qr_io, format='PNG')
            qr_io.seek(0)
            zip_file.writestr(f"{obj.id}_QRCode.png", qr_io.read())
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="qr_codes.zip"'
    messages.success(request, f"QR codes for {queryset.count()} records were successfully generated and downloaded.")
    return response


class Useradmin(admin.ModelAdmin):
    list_display=['username','email','phone_no']
admin.site.register(CustomUser,Useradmin)  


def set_fixed_price(modeladmin,request,queryset):
    fixed_price=100.0
    updated_count=queryset.update(cost=fixed_price)
    modeladmin.message_user(request, f'Successfully updated {updated_count} URL(s) to the fixed price of {fixed_price}')


class UniqueurlAdmin(admin.ModelAdmin):
    list_display=['user','created_at','cost','in_cart']
    actions=[generate_qr_codes]
    change_list_template = "urls/url.html"

admin.site.register(UniqueURL,UniqueurlAdmin)


class PaymentAdmin(admin.ModelAdmin):
    list_display=['user','transaction_id','status','created_at','checkout_id']
admin.site.register(Payment, PaymentAdmin)


class ContactQueryAdmin(admin.ModelAdmin):
    list_display=['name','email','message','created_at']
admin.site.register(ContactQuery,ContactQueryAdmin)


class CartItemAdmin(admin.ModelAdmin):
    list_display=['user','quantity','total_price','is_closed']
    filter_horizontal=['unique_url', ]
admin.site.register(CartItem, CartItemAdmin)


class DetailsAdmin(admin.ModelAdmin):
    list_display=['unique_url','title','description']
admin.site.register(Details,DetailsAdmin)


class ImagesAdmin(admin.ModelAdmin):
    list_display=['file','detail','created_at']
admin.site.register(Images,ImagesAdmin)



