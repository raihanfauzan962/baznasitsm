# dashboard/admin.py
from django.contrib import admin
from .models import TicketSummary

@admin.register(TicketSummary)
class TicketSummaryAdmin(admin.ModelAdmin):
    list_display = (
        'incident_open', 'incident_assigned', 'incident_in_progress',
        'incident_pending', 'incident_resolved', 'incident_closed',
        'service_pending', 'service_approved', 'service_rejected', 'last_updated'
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
