from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
import string
import random
from .models import CustomUser,UniqueURL,Payment,ContactQuery,CartItem,Details


# Register your models here.
@admin.action(description="generate qr codes")
def generate_qr_codes(modeladmin, request, queryset):
    selected_ids = queryset.values_list('id', flat=True)
    ids = ",".join(map(str, selected_ids))
    return HttpResponseRedirect(reverse('download_qr_codes') + f"?ids={ids}")


class Useradmin(admin.ModelAdmin):
    list_display=['username','email','phn_no']
    actions=[generate_qr_codes]
admin.site.register(CustomUser,Useradmin)  


def generate_random_url(length=10):
     return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
def generate_50_urls(modeladmin,request,queryset):
    users=CustomUser.objects.all()
    for user in users:
        for _ in range(50):
            random_url = f"https://example.com/{generate_random_url()}"
            UniqueURL.objects.create(user=user,url=random_url)
generate_50_urls.short_description = "Generated 50 random URLs for all users"



class UniqueurlAdmin(admin.ModelAdmin):
    list_display=['url','created_at','cost']
    actions=[generate_50_urls]
admin.site.register(UniqueURL,UniqueurlAdmin)


def set_fixed_price(modeladmin,request,queryset):
    fixed_price=100.0
    updated_count=queryset.update(cost=fixed_price)
    modeladmin.message_user(request, f'Successfully updated {updated_count} URL(s) to the fixed price of {fixed_price}')



class PaymentAdmin(admin.ModelAdmin):
    list_display=['user','transaction_id','status','created_at']
admin.site.register(Payment, PaymentAdmin)


class ContactQueryAdmin(admin.ModelAdmin):
    list_display=['name','email','message','created_at']
admin.site.register(ContactQuery,ContactQueryAdmin)

admin.site.register(CartItem)
admin.site.register(Details)