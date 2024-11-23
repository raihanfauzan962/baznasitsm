# dashboard/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from incident_report.models import IncidentReport
from service_request.models import ServiceRequest
from .models import TicketSummary

# Helper function to update the TicketSummary counts
def update_ticket_summary():
    summary, created = TicketSummary.objects.get_or_create(id=1)
    summary.update_counts()

@receiver(post_save, sender=IncidentReport)
def update_ticket_summary_incident(sender, instance, **kwargs):
    update_ticket_summary()

@receiver(post_save, sender=ServiceRequest)
def update_ticket_summary_service(sender, instance, **kwargs):
    update_ticket_summary()
