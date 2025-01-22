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
from .models import CustomUser,UniqueURL,Payment,ContactQuery,CartItem,Details


# Register your models here.
@admin.action(description="generate qr codes")
def generate_qr_codes(modeladmin, request, queryset):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as zip_file:
        for obj in queryset:
            qr = qrcode.make(f"http://localhost:8000/api/vi/url/{obj.id}/details")
            qr_io = io.BytesIO()
            qr.save(qr_io, format='PNG')
            qr_io.seek(0)
            zip_file.writestr(f"{obj.username}_QRCode.png", qr_io.read())
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="qr_codes.zip"'
    messages.success(request, f"QR codes for {queryset.count()} records were successfully generated and downloaded.")
    return response


class Useradmin(admin.ModelAdmin):
    list_display=['username','email','phn_no']
    actions=[generate_qr_codes]

admin.site.register(CustomUser,Useradmin)  


def set_fixed_price(modeladmin,request,queryset):
    fixed_price=100.0
    updated_count=queryset.update(cost=fixed_price)
    modeladmin.message_user(request, f'Successfully updated {updated_count} URL(s) to the fixed price of {fixed_price}')


class UniqueurlAdmin(admin.ModelAdmin):
    list_display=['user','created_at','cost']
    change_list_template = "urls/url.html"

admin.site.register(UniqueURL,UniqueurlAdmin)


class PaymentAdmin(admin.ModelAdmin):
    list_display=['user','transaction_id','status','created_at']
admin.site.register(Payment, PaymentAdmin)


class ContactQueryAdmin(admin.ModelAdmin):
    list_display=['name','email','message','created_at']
admin.site.register(ContactQuery,ContactQueryAdmin)

class CartItemAdmin(admin.ModelAdmin):
    list_display=['user','quantity','total_price']
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Details)



# # admin.py
# from django.contrib import admin
# from django.urls import path
# from django.http import HttpResponseRedirect
# from django_admin_extra_buttons.mixins import ExtraButtonsMixin
# from .models import CustomUser
# from .utils import generate_50_urls  # Assuming your generate_50_urls function is defined elsewhere

# # Define your custom view
# def generate_50_urls_action(modeladmin, request, queryset):
#     # Call your custom function
#     generate_50_urls(modeladmin, request, queryset)
#     modeladmin.message_user(request, "50 URLs generated successfully!")
#     return HttpResponseRedirect(request.path)

# # Admin class using ExtraButtonsMixin
# class UserAdmin(ExtraButtonsMixin, admin.ModelAdmin):
#     list_display = ['username', 'email', 'phn_no']
#     actions = [generate_50_urls_action]

#     extra_buttons = [
#         {
#             'label': 'Generate 50 URLs',  # The label for the button
#             'url': 'generate_50_urls_action',  # The action to call
#             'icon': 'fa fa-qrcode',  # Optional: FontAwesome icon
#             'confirm': True,  # Optional: Ask for confirmation before triggering the action
#         }
#     ]

#     def get_urls(self):
#         # Add custom URL for your custom action
#         urls = super().get_urls()
#         custom_urls = [
#             path('generate_50_urls_action/', self.admin_site.admin_view(generate_50_urls_action)),
#         ]
#         return custom_urls + urls

# # Register your model and the custom admin class
# admin.site.register(CustomUser, UserAdmin)
