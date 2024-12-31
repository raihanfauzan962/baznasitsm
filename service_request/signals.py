from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import ServiceRequest

# Signal to notify the user, assignee, and group when the status of a service request changes
@receiver(post_save, sender=ServiceRequest)
def notify_on_status_change(sender, instance, created, **kwargs):
    if not created:  # Only check for updates (not creation)
        dirty_fields = instance.get_dirty_fields()
        if 'status' in dirty_fields:  # Check if the status field has changed
            subject = f"Your Service Request {instance.ticket_code} is now {instance.get_status_display()}"

            message = (
                f"Dear {instance.user.get_full_name()},\n\n"
                f"Your service request for {instance.service_item.name} has been "
                f"{instance.get_status_display()}.\n\n"
                f"Ticket Code: {instance.ticket_code}\n"
                f"Service Item: {instance.service_item.name}\n"
                f"Status: {instance.get_status_display()}\n\n"
                f"Thank you for using our service."
            )

            # Send email to the user who created the service request
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,  # From email
                [instance.user.email],  # To email
                fail_silently=False,
            )

            # Send email to the assignee (if any)
            if instance.assignee:
                assignee_message = (
                    f"Dear {instance.assignee.get_full_name()},\n\n"
                    f"You are assigned to the service request {instance.ticket_code} "
                    f"for {instance.service_item.name}, which is now {instance.get_status_display()}.\n\n"
                    f"Ticket Code: {instance.ticket_code}\n"
                    f"Service Item: {instance.service_item.name}\n"
                    f"Status: {instance.get_status_display()}\n\n"
                    f"Please check the admin dashboard for further details."
                )

                send_mail(
                    subject,
                    assignee_message,
                    settings.EMAIL_HOST_USER,  # From email
                    [instance.assignee.email],  # To email
                    fail_silently=False,
                )

            # Send email to all users in the group (if any group is assigned)
            if instance.group:
                group_users = instance.group.user_set.all()
                for user in group_users:
                    group_message = (
                        f"Dear {user.get_full_name()},\n\n"
                        f"A service request {instance.ticket_code} for {instance.service_item.name} "
                        f"has been updated to {instance.get_status_display()}.\n\n"
                        f"Ticket Code: {instance.ticket_code}\n"
                        f"Service Item: {instance.service_item.name}\n"
                        f"Status: {instance.get_status_display()}\n\n"
                        f"Please check the admin dashboard for further details."
                    )

                    send_mail(
                        subject,
                        group_message,
                        settings.EMAIL_HOST_USER,  # From email
                        [user.email],  # To email
                        fail_silently=False,
                    )
