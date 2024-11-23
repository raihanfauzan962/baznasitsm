# incident_report/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import IncidentReport

@receiver(post_save, sender=IncidentReport)
def notify_user_on_assignment(sender, instance, created, **kwargs):
    # Existing logic for notifying when assigned
    if instance.assigned_to:
        subject = f'Ticket Assigned: {instance.ticket_code}'
        message = f'Hello {instance.assigned_to.get_full_name()},\n\n' \
                  f'You have been assigned a new ticket with the following details:\n' \
                  f'Subject: {instance.subject}\n' \
                  f'Description: {instance.description}\n' \
                  f'Status: {instance.get_status_display()}\n\n' \
                  f'Please log in to the system to view more details.'

        # Send email notification to the assigned user
        send_mail(
            subject,
            message,
            'najocode@gmail.com',  # From email
            [instance.assigned_to.email],  # To email
            fail_silently=False,
        )

@receiver(post_save, sender=IncidentReport)
def notify_requester_on_status_update(sender, instance, created, **kwargs):
    if not created:
        # Check if the status field has changed
        dirty_fields = instance.get_dirty_fields()
        if 'status' in dirty_fields:
            # Define the common email subject
            subject = f'Ticket Status Updated: {instance.ticket_code}'

            # Message for the primary requester
            requester_message = f'Hello {instance.requester.get_full_name()},\n\n' \
                                f'The status of your ticket has been updated:\n' \
                                f'Subject: {instance.subject}\n' \
                                f'New Status: {instance.get_status_display()}\n\n' \
                                f'Please log in to the system to view more details.'

            # Message for the "request_for" email
            requester_for_message = f'Hello,\n\n' \
                                    f'The status of the ticket you were marked as a contact for has been updated:\n' \
                                    f'Subject: {instance.subject}\n' \
                                    f'New Status: {instance.get_status_display()}\n\n' \
                                    f'Please log in to the system to view more details.'

            # Send email to primary requester
            send_mail(
                subject,
                requester_message,
                'najocode@gmail.com',  # From email
                [instance.requester.email],  # To requester email
                fail_silently=False,
            )

            # If 'request_for' email is filled, send a different message to that email
            if instance.request_for:
                send_mail(
                    subject,
                    requester_for_message,
                    'najocode@gmail.com',  # From email
                    [instance.request_for],  # To requester_for email
                    fail_silently=False,
                )