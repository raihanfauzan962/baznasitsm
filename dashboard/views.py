from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from incident_report.models import IncidentReport
from service_request.models import ServiceRequest

class UserDashboardView(LoginRequiredMixin, View):
    template_name = 'dashboard/user_dashboard.html'

    def get(self, request):
        # Fetching all incident reports for the logged-in user
        incident_reports = IncidentReport.objects.filter(requester=request.user)

        # Fetching all service requests for the logged-in user
        service_requests = ServiceRequest.objects.filter(user=request.user)

        # Count the total number of tickets
        total_incidents = incident_reports.count()
        total_service_requests = service_requests.count()

        # Count incidents by status
        incident_status_counts = {
            'open': incident_reports.filter(status='Open').count(),
            'assigned': incident_reports.filter(status='Assigned').count(),
            'in_progress': incident_reports.filter(status='In Progress').count(),
            'pending': incident_reports.filter(status='Pending').count(),
            'resolved': incident_reports.filter(status='Resolved').count(),
            'closed': incident_reports.filter(status='Closed').count(),
        }

        # Count service requests by status
        service_request_status_counts = {
            'pending': service_requests.filter(status='pending').count(),
            'approved': service_requests.filter(status='approved').count(),
            'rejected': service_requests.filter(status='rejected').count(),
        }

        context = {
            'incident_reports': incident_reports,
            'service_requests': service_requests,
            'total_incidents': total_incidents,
            'total_service_requests': total_service_requests,
            'incident_status_counts': incident_status_counts,
            'service_request_status_counts': service_request_status_counts,
        }

        return render(request, self.template_name, context)
