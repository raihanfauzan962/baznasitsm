# dashboard/models.py
from django.db import models
from incident_report.models import IncidentReport
from service_request.models import ServiceRequest

class TicketSummary(models.Model):
    incident_open = models.IntegerField(default=0)
    incident_assigned = models.IntegerField(default=0)
    incident_in_progress = models.IntegerField(default=0)
    incident_pending = models.IntegerField(default=0)
    incident_resolved = models.IntegerField(default=0)
    incident_closed = models.IntegerField(default=0)

    service_pending = models.IntegerField(default=0)
    service_approved = models.IntegerField(default=0)
    service_rejected = models.IntegerField(default=0)

    last_updated = models.DateTimeField(auto_now=True)

    def update_counts(self):
        self.incident_open = IncidentReport.objects.filter(status='Open').count()
        self.incident_assigned = IncidentReport.objects.filter(status='Assigned').count()
        self.incident_in_progress = IncidentReport.objects.filter(status='In Progress').count()
        self.incident_pending = IncidentReport.objects.filter(status='Pending').count()
        self.incident_resolved = IncidentReport.objects.filter(status='Resolved').count()
        self.incident_closed = IncidentReport.objects.filter(status='Closed').count()

        self.service_pending = ServiceRequest.objects.filter(status='pending').count()
        self.service_approved = ServiceRequest.objects.filter(status='approved').count()
        self.service_rejected = ServiceRequest.objects.filter(status='rejected').count()

        self.save()

    def __str__(self):
        return "Ticket Summary"
