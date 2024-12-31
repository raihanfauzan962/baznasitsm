# incident_report/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.utils.html import strip_tags
from .models import IncidentReport


@receiver(post_save, sender=IncidentReport)
def notify_users_on_changes(sender, instance, created, **kwargs):
    """
    Signal to notify users about changes in:
    - Assigned group
    - Assigned user (assignee)
    - Status updates
    """
    # Fetch dirty fields (requires a library like django-dirtyfields)
    dirty_fields = instance.get_dirty_fields()

    # Notify group members if the group changes
    if 'group' in dirty_fields:
        if instance.group:
            group_members = instance.group.user_set.all()
            subject = f'Ticket Updated: {instance.ticket_code}'
            message = f'Hello,\n\n' \
                      f'The ticket "{instance.ticket_code}" has been reassigned to your group ({instance.group.name}).\n' \
                      f'Please check the system for details.\n\n' \
                      f'Subject: {instance.subject}\n' \
                      f'Description: {instance.description}\n' \
                      f'Status: {instance.get_status_display()}'

            recipient_list = [user.email for user in group_members]
            send_mail(
                subject,
                message,
                'najocode@gmail.com',  # From email
                recipient_list,
                fail_silently=False,
            )

    # Notify the newly assigned user (assignee) if `assigned_to` changes
    if 'assigned_to' in dirty_fields and instance.assigned_to:
        subject = f'Ticket Assigned to You: {instance.ticket_code}'
        message = f'Hello {instance.assigned_to.get_full_name()},\n\n' \
                  f'You have been assigned a ticket with the following details:\n' \
                  f'Subject: {instance.subject}\n' \
                  f'Description: {instance.description}\n' \
                  f'Status: {instance.get_status_display()}.\n\n' \
                  f'Please log in to the system to view more details.'

        send_mail(
            subject,
            message,
            'najocode@gmail.com',  # From email
            [instance.assigned_to.email],  # To email
            fail_silently=False,
        )

    # Notify group members and the assignee on status updates
    if 'status' in dirty_fields:
        subject = f'Ticket Status Updated: {instance.ticket_code}'
        message = f'The status of the ticket "{instance.ticket_code}" has been updated.\n\n' \
                  f'Subject: {instance.subject}\n' \
                  f'New Status: {instance.get_status_display()}\n\n' \
                  f'Please check the system for details.'

        # Notify group members
        if instance.group:
            group_members = instance.group.user_set.all()
            recipient_list = [user.email for user in group_members]
            send_mail(
                subject,
                message,
                'najocode@gmail.com',  # From email
                recipient_list,
                fail_silently=False,
            )

        # Notify assignee
        if instance.assigned_to:
            send_mail(
                subject,
                message,
                'najocode@gmail.com',  # From email
                [instance.assigned_to.email],  # To email
                fail_silently=False,
            )
