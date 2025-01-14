from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import CustomUser,UniqueURL,Payment,ContactQuery


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

class UniqueurlAdmin(admin.ModelAdmin):
    list_display=['description','url','created_at']
admin.site.register(UniqueURL,UniqueurlAdmin)



class PaymentAdmin(admin.ModelAdmin):
    list_display=['user','amount','transaction_id','status','created_at']
admin.site.register(Payment, PaymentAdmin)


class ContactQueryAdmin(admin.ModelAdmin):
    list_display=['name','email','message','created_at']
admin.site.register(ContactQuery,ContactQueryAdmin)


