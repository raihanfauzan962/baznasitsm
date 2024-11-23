from django.contrib import admin
from .models import Category, Asset, AssetForm, ServiceRequest
from django import forms
import json
from django.core.exceptions import ValidationError
import csv
from django.http import HttpResponse
from .models import ServiceRequest

class AssetFormAdminForm(forms.ModelForm):
    form_fields = forms.CharField(
        widget=forms.Textarea,
        help_text="Enter JSON formatted form fields",
        label="Form Fields"
    )

    class Meta:
        model = AssetForm
        fields = '__all__'

    def clean_form_fields(self):
        data = self.cleaned_data['form_fields']
        try:
            json_data = json.loads(data)
            return json_data
        except json.JSONDecodeError:
            raise ValidationError("Invalid JSON format. Please enter valid JSON.")

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']  # Enable search by category name

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'pic']
    list_filter = ['category']  # Enable filtering by category
    search_fields = ['name']  # Enable search by asset name
    fields = ['name', 'category', 'pic', 'image']

@admin.register(AssetForm)
class AssetFormAdmin(admin.ModelAdmin):
    form = AssetFormAdminForm
    list_display = ['asset']
    search_fields = ['asset__name']  # Enable search by asset name through the related model
    list_filter = ['asset']  # Enable filtering by asset

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ['ticket_code', 'asset', 'user', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'asset__name']
    actions = ['export_to_csv']  # Register the action

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        # Allow superusers to see all service requests
        if request.user.is_superuser:
            return qs

        # If the user is staff, filter by assets where the user is PIC
        if request.user.is_staff:
            return qs.filter(asset__pic=request.user)

        return qs  # Return all requests for other cases

    def export_to_csv(self, request, queryset):
        # CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="service_requests.csv"'
        
        writer = csv.writer(response)
        # Writing header row
        writer.writerow(['Ticket Code', 'Category', 'Asset', 'PIC', 'Status', 'Created At', 'Approved At', 'Rejected At', 'Form Data'])

        for service_request in queryset:
            # Extracting data from each service request
            ticket_code = service_request.ticket_code
            category = service_request.asset.category.name if service_request.asset and service_request.asset.category else 'N/A'
            asset = service_request.asset.name if service_request.asset else 'N/A'
            pic = service_request.asset.pic.username if service_request.asset and service_request.asset.pic else 'N/A'
            status = service_request.get_status_display()
            created_at = service_request.created_at.strftime("%Y-%m-%d %H:%M:%S")
            approved_at = service_request.approved_at.strftime("%Y-%m-%d %H:%M:%S") if service_request.approved_at else 'Not Approved'
            rejected_at = service_request.rejected_at.strftime("%Y-%m-%d %H:%M:%S") if service_request.rejected_at else 'Not Rejected'
            form_data = json.dumps(service_request.form_data) if service_request.form_data else 'No form data available'

            # Writing a row for each service request
            writer.writerow([ticket_code, category, asset, pic, status, created_at, approved_at, rejected_at, form_data])

        return response

    export_to_csv.short_description = "Export selected service requests to CSV"


