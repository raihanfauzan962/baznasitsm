from django.contrib import admin
from .models import Category, ServiceItem, ServiceItemForm, ServiceRequest, Group, User
from django import forms
import json
from django.core.exceptions import ValidationError
import csv
from django.http import HttpResponse
from django.utils.safestring import mark_safe

class ServiceItemFormAdminForm(forms.ModelForm):
    form_fields = forms.CharField(
        widget=forms.Textarea,
        help_text="Enter JSON formatted form fields",
        label="Form Fields"
    )

    class Meta:
        model = ServiceItemForm
        fields = '__all__'

    def clean_form_fields(self):
        data = self.cleaned_data['form_fields']
        try:
            json_data = json.loads(data)
            return json_data
        except json.JSONDecodeError:
            raise ValidationError("Invalid JSON format. Please enter valid JSON.")

# Admin for Category
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']  # Enable search by category name

# Admin for ServiceItem
@admin.register(ServiceItem)
class ServiceItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'image']
    list_filter = ['category']  # Enable filtering by category
    search_fields = ['name']  # Enable search by service item name
    fields = ['name', 'category', 'image']  # Corrected to use 'image' instead of 

# Admin for ServiceItemForm
@admin.register(ServiceItemForm)
class ServiceItemFormAdmin(admin.ModelAdmin):
    form = ServiceItemFormAdminForm
    list_display = ['service_item']
    search_fields = ['service_item__name']  # Enable search by service item name through the related model
    list_filter = ['service_item']  # Enable filtering by service item

# Custom form for ServiceRequestAdmin to filter assignee based on the selected group
class ServiceRequestAdminForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If the instance has a group assigned, filter assignee field
        if self.instance.pk:  # Instance is being edited (not new)
            group = self.instance.group
            if group:
                self.fields['assignee'].queryset = group.user_set.all()  # Filter assignee to users in this group
        else:
            # If the instance is new, leave the assignee queryset unfiltered
            self.fields['assignee'].queryset = User.objects.none()  # Initially empty until group is set

# Admin for ServiceRequest
@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    form = ServiceRequestAdminForm
    list_display = ['ticket_code', 'service_item', 'user', 'status', 'group', 'assignee', 'created_at', 'formatted_form_data']
    list_filter = ['status', 'created_at', 'group', 'assignee']
    search_fields = ['user__username', 'service_item__name']
    actions = ['export_to_csv']

    def formatted_form_data(self, obj):
        """
        Display the JSON form_data field as a formatted HTML table.
        """
        if not obj.form_data:
            return "No form data available"
        
        table_html = "<table border='1' style='border-collapse: collapse; width: 100%;'>"
        table_html += "<tr><th>Field</th><th>Value</th></tr>"
        
        for key, value in obj.form_data.items():
            table_html += f"<tr><td>{key}</td><td>{value}</td></tr>"
        
        table_html += "</table>"
        return mark_safe(table_html)  # Mark the table as safe HTML to render it correctly in the admin

    formatted_form_data.short_description = "Form Data (Table)"  # Set column title for the admin

    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="service_requests.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Ticket Code', 'Category', 'Service Item', 'Image', 'Group', 'Assignee', 'Status', 'Created At', 'Approved At', 'Rejected At', 'Form Data'])
        
        for service_request in queryset:
            ticket_code = service_request.ticket_code
            category = service_request.service_item.category.name if service_request.service_item and service_request.service_item.category else 'N/A'
            service_item = service_request.service_item.name if service_request.service_item else 'N/A'
            image = service_request.service_item.image.url if service_request.service_item.image else 'No Image'
            group = service_request.group.name if service_request.group else 'N/A'
            assignee = service_request.assignee.username if service_request.assignee else 'N/A'
            status = service_request.get_status_display()
            created_at = service_request.created_at.strftime("%Y-%m-%d %H:%M:%S")
            approved_at = service_request.approved_at.strftime("%Y-%m-%d %H:%M:%S") if service_request.approved_at else 'Not Approved'
            rejected_at = service_request.rejected_at.strftime("%Y-%m-%d %H:%M:%S") if service_request.rejected_at else 'Not Rejected'
            form_data = json.dumps(service_request.form_data) if service_request.form_data else 'No form data available'

            writer.writerow([ticket_code, category, service_item, image, group, assignee, status, created_at, approved_at, rejected_at, form_data])

        return response

    export_to_csv.short_description = "Export selected service requests to CSV"

    def save_model(self, request, obj, form, change):
        if obj.group:
            if not obj.assignee or obj.assignee not in obj.group.user_set.all():
                obj.assignee = None
        super().save_model(request, obj, form, change)

