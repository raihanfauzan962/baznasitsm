from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin

from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from .models import IncidentReport, SubCategory, Issue, AffectedDevice, Floor
from .forms import IncidentReportForm

from django.http import JsonResponse

from django.utils import timezone
from datetime import timedelta

class CreateIncidentReportView(LoginRequiredMixin, CreateView):
    model = IncidentReport
    form_class = IncidentReportForm
    template_name = 'incident_report/incident_report_form.html'

    def form_valid(self, form):
        # Ensure the user is authenticated
        if self.request.user.is_authenticated:
            form.instance.requester = self.request.user  # Pre-fill requester
        else:
            # Handle unauthenticated user case
            form.add_error(None, "You must be logged in to submit a report.")
            return self.form_invalid(form)

        self.object = form.save()  # Save the form and get the object
        return redirect(reverse('report_detail', kwargs={'pk': self.object.pk}))  # Redirect to the detail view

class IncidentReportDetailView(LoginRequiredMixin, DetailView):
    model = IncidentReport
    template_name = 'incident_report/report_detail.html'
    context_object_name = 'report'


class UserReportsListView(ListView):
    model = IncidentReport
    template_name = 'incident_report/user_reports.html'
    context_object_name = 'reports'

    def get_queryset(self):
        queryset = IncidentReport.objects.filter(requester=self.request.user)
        
        # Filtering logic
        filter_option = self.request.GET.get('filter', 'all')
        status_filter = self.request.GET.get('status', 'all')
        today = timezone.now().date()
        start_date = None

        # Date range filtering
        if filter_option == 'today':
            start_date = today
        elif filter_option == 'yesterday':
            start_date = today - timedelta(days=1)
        elif filter_option == '7_days':
            start_date = today - timedelta(days=7)
        elif filter_option == '30_days':
            start_date = today - timedelta(days=30)

        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)

        # Status filtering
        if status_filter and status_filter != 'all':
            queryset = queryset.filter(status=status_filter)

        return queryset.order_by('-created_at')

# ajax views
def load_subcategories(request):
    category_id = request.GET.get('category')
    subcategories = SubCategory.objects.filter(category_id=category_id).all()
    return JsonResponse(list(subcategories.values('id', 'name')), safe=False)

def load_issues(request):
    sub_category_id = request.GET.get('sub_category')
    issues = Issue.objects.filter(sub_category_id=sub_category_id).all()
    return JsonResponse(list(issues.values('id', 'name')), safe=False)

def load_affected_devices(request):
    issue_id = request.GET.get('issue')
    affected_devices = AffectedDevice.objects.filter(issue_id=issue_id).all()
    return JsonResponse(list(affected_devices.values('id', 'name')), safe=False)

def load_floors(request):
    building_id = request.GET.get('building')
    floors = Floor.objects.filter(building_id=building_id).all()
    return JsonResponse(list(floors.values('id', 'name')), safe=False)