from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ContactQuery
from django.conf import settings
from django.core.mail import send_mail


#signals for feedback
@receiver(post_save, sender=ContactQuery)
def send_contact_email_to_admin(sender, instance, created, **kwargs):
    if created:
        subject = f"New Contact Query from {instance.name}"
        admin_message = (
            f"You have received a new query/feedback from {instance.name}.\n\n"
            f"Details:\n"
            f"Name: {instance.name}\n"
            f"Email: {instance.email}\n"
            f"Message:\n{instance.message}\n\n"
            f"Submitted on: {instance.created_at}"
        )
        send_mail(
            subject,
            admin_message,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            from_email=instance.email
        )