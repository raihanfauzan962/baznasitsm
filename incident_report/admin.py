from django.contrib import admin
from django.http import HttpResponse
from django.db import models 
import csv
from .models import Category, SubCategory, Issue, AffectedDevice, Building, Floor, IncidentReport

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)

class IssueAdmin(admin.ModelAdmin):
    list_display = ('name', 'sub_category')
    list_filter = ('sub_category',)
    search_fields = ('name',)

class AffectedDeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'issue')
    list_filter = ('issue',)
    search_fields = ('name',)

class BuildingAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class FloorAdmin(admin.ModelAdmin):
    list_display = ('name', 'building')
    list_filter = ('building',)
    search_fields = ('name',)

class IncidentReportAdmin(admin.ModelAdmin):
    list_display = ('ticket_code', 'subject', 'status', 'requester', 'assigned_to', 'created_at')
    list_filter = ('status', 'created_at', 'building', 'floor', 'assigned_to')
    search_fields = ('ticket_code', 'subject', 'requester__email')
    actions = ['export_incident_reports_to_csv']

    def export_incident_reports_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="incident_reports.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Ticket Code', 'Requester', 'Request For', 'Contact Person', 'Category',
            'Sub Category', 'Issue', 'Affected Device', 'Building', 'Floor',
            'Subject', 'Description', 'Status', 'Assigned To', 'Created At', 'Assigned At',
            'Resolved At', 'Closed At'
        ])

        for report in queryset:
            writer.writerow([
                report.ticket_code,
                report.requester.email,
                report.request_for,
                report.contact_person,
                report.category,
                report.sub_category,
                report.issue,
                report.affected_device,
                report.building,
                report.floor,
                report.subject,
                report.description,
                report.get_status_display(),
                report.assigned_to.email if report.assigned_to else 'Not Assigned',
                report.created_at,
                report.assigned_at if report.assigned_at else 'Not Assigned',
                report.resolved_at if report.resolved_at else 'Not Resolved',
                report.closed_at if report.closed_at else 'Not Closed'
            ])

        return response

    export_incident_reports_to_csv.short_description = "Export Selected Reports to CSV"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs

        if request.user.is_staff:
            return qs.filter(assigned_to=request.user)

        return qs

    def change_list(self, request, queryset):
        # Get the base queryset
        queryset = self.get_queryset(request)

        # Get the total count
        total_count = queryset.count()

        # Get counts based on status
        status_counts = queryset.values('status').annotate(count=models.Count('id'))

        # Prepare a dictionary for the status counts
        status_count_dict = {status['status']: status['count'] for status in status_counts}

        # Add these counts to the context
        context = {
            'total_count': total_count,
            'status_counts': status_count_dict,
        }

        # Render the change list with the extra context
        return super().change_list(request, queryset, extra_context=context)


admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(AffectedDevice, AffectedDeviceAdmin)
admin.site.register(Building, BuildingAdmin)
admin.site.register(Floor, FloorAdmin)
admin.site.register(IncidentReport, IncidentReportAdmin)