from django.contrib import admin
from django.http import HttpResponse
from django import forms
from django.db import models
from django.core.exceptions import ValidationError
import csv
from .models import (
    Category,
    SubCategory,
    Issue,
    AffectedDevice,
    Building,
    Floor,
    IncidentReport,
    User,
    Group
)

# Admin for Category
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Admin for SubCategory
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)

# Admin for Issue
class IssueAdmin(admin.ModelAdmin):
    list_display = ('name', 'sub_category')
    list_filter = ('sub_category',)
    search_fields = ('name',)

# Admin for AffectedDevice
class AffectedDeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'issue')
    list_filter = ('issue',)
    search_fields = ('name',)

# Admin for Building
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Admin for Floor
class FloorAdmin(admin.ModelAdmin):
    list_display = ('name', 'building')
    list_filter = ('building',)
    search_fields = ('name',)

# Custom form for IncidentReportAdmin to filter `assigned_to` based on the selected group
class IncidentReportAdminForm(forms.ModelForm):
    class Meta:
        model = IncidentReport
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:  # Editing an existing instance
            group = self.instance.group
            if group:
                self.fields['assigned_to'].queryset = group.user_set.all()
        else:
            # If creating a new instance, `assigned_to` will initially be empty
            self.fields['assigned_to'].queryset = User.objects.none()

# Admin for IncidentReport
class IncidentReportAdmin(admin.ModelAdmin):
    form = IncidentReportAdminForm
    list_display = (
        'ticket_code', 'subject', 'status', 'requester', 'group', 'assigned_to', 'created_at'
    )
    list_filter = (
        'status', 'created_at', 'building', 'floor', 'group', 'assigned_to',
        'open_at', 'pending_at', 'pending_customer_at', 'pending_assignment_at',
        'pending_third_party_at', 'pending_procurement_at', 'assigned_at',
        'resolved_at', 'cancelled_at', 'waiting_approval_at', 'approved_at',
        'rejected_at', 'closed_at'
    )
    search_fields = ('ticket_code', 'subject', 'requester__email')
    actions = ['export_incident_reports_to_csv']

    def export_incident_reports_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="incident_reports.csv"'

        writer = csv.writer(response)
        # Header row with all statuses
        writer.writerow([
            'Ticket Code', 'Requester', 'Request For', 'Contact Person', 'Category',
            'Sub Category', 'Issue', 'Affected Device', 'Building', 'Floor',
            'Subject', 'Description', 'Status', 'Assigned To', 'Created At',
            'Open At', 'Pending At', 'Pending Customer At', 'Pending Assignment At',
            'Pending Third Party At', 'Pending Procurement At', 'Assigned At',
            'Resolved At', 'Cancelled At', 'Waiting Approval At', 'Approved At',
            'Rejected At', 'Closed At'
        ])

        # Data rows with all timestamps
        for report in queryset:
            writer.writerow([
                report.ticket_code,
                report.requester.email if report.requester else 'N/A',
                report.request_for or 'N/A',
                report.contact_person or 'N/A',
                report.category.name if report.category else 'N/A',
                report.sub_category.name if report.sub_category else 'N/A',
                report.issue.name if report.issue else 'N/A',
                report.affected_device.name if report.affected_device else 'N/A',
                report.building.name if report.building else 'N/A',
                report.floor.name if report.floor else 'N/A',
                report.subject,
                report.description or 'N/A',
                report.get_status_display(),
                report.assigned_to.email if report.assigned_to else 'Not Assigned',
                report.created_at,
                report.open_at or 'Not Opened',
                report.pending_at or 'Not Pending',
                report.pending_customer_at or 'Not Pending Customer',
                report.pending_assignment_at or 'Not Pending Assignment',
                report.pending_third_party_at or 'Not Pending Third Party',
                report.pending_procurement_at or 'Not Pending Procurement',
                report.assigned_at or 'Not Assigned',
                report.resolved_at or 'Not Resolved',
                report.cancelled_at or 'Not Cancelled',
                report.waiting_approval_at or 'Not Waiting Approval',
                report.approved_at or 'Not Approved',
                report.rejected_at or 'Not Rejected',
                report.closed_at or 'Not Closed'
            ])

        return response

    export_incident_reports_to_csv.short_description = "Export Selected Reports to CSV"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.is_staff:
            return qs.filter(assigned_to=request.user)
        return qs.none()  # Regular users can't access the admin

    def save_model(self, request, obj, form, change):
        if obj.group:
            if not obj.assigned_to or obj.assigned_to not in obj.group.user_set.all():
                obj.assigned_to = None
        super().save_model(request, obj, form, change)


admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(AffectedDevice, AffectedDeviceAdmin)
admin.site.register(Building, BuildingAdmin)
admin.site.register(Floor, FloorAdmin)
admin.site.register(IncidentReport, IncidentReportAdmin)
