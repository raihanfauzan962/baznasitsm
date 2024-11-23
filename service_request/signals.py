from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import ServiceRequest

# Signal to notify the PIC when a service request is created
@receiver(post_save, sender=ServiceRequest)
def notify_pic_on_request_creation(sender, instance, created, **kwargs):
    if created:  # Only send email when the service request is created
        asset = instance.asset
        if asset.pic:  # Ensure the asset has a PIC assigned
            subject = f"New Service Request for {asset.name}"
            message = (
                f"Dear {asset.pic.get_full_name()},\n\n"
                f"A new service request has been created by {instance.user.username} "
                f"for the asset {asset.name}.\n\n"
                f"Request Details:\n"
                f"Ticket Code: {instance.ticket_code}\n"
                f"Asset: {asset.name}\n"
                f"Status: {instance.get_status_display()}\n\n"
                f"Please check the admin dashboard for further details."
            )

            # Send email notification to the PIC
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,  # From email
                [asset.pic.email],  # To email
                fail_silently=False,
            )

# Signal to notify the user when the status of a service request changes
@receiver(post_save, sender=ServiceRequest)
def notify_user_on_status_change(sender, instance, created, **kwargs):
    if not created:  # Only check for updates (not creation)
        dirty_fields = instance.get_dirty_fields()
        if 'status' in dirty_fields:  # Check if the status field has changed
            subject = f"Your Service Request {instance.ticket_code} is now {instance.get_status_display()}"
            message = (
                f"Dear {instance.user.get_full_name()},\n\n"
                f"Your service request for {instance.asset.name} has been "
                f"{instance.get_status_display()}.\n\n"
                f"Ticket Code: {instance.ticket_code}\n"
                f"Asset: {instance.asset.name}\n"
                f"Status: {instance.get_status_display()}\n\n"
                f"Thank you for using our service."
            )

            # Send email notification to the user
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,  # From email
                [instance.user.email],  # To email
                fail_silently=False,
            )
