from django import forms
from django.core.exceptions import ValidationError
from .models import IncidentReport, SubCategory, Issue, AffectedDevice, Floor
import os

class IncidentReportForm(forms.ModelForm):
    class Meta:
        model = IncidentReport
        fields = [
            'request_for', 'contact_person', 'category', 'sub_category', 
            'issue', 'affected_device', 'building', 'floor', 'subject', 
            'description', 'attachment'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6, 'class': 'form-control', 'placeholder': 'Describe the incident'}),
            'request_for': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter their email'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter WhatsApp number'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'sub_category': forms.Select(attrs={'class': 'form-control'}),
            'issue': forms.Select(attrs={'class': 'form-control'}),
            'affected_device': forms.Select(attrs={'class': 'form-control'}),
            'building': forms.Select(attrs={'class': 'form-control'}),
            'floor': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject of the report'}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize sub_category, issue, affected_device, floor with empty queryset
        self.fields['sub_category'].queryset = SubCategory.objects.none()
        self.fields['issue'].queryset = Issue.objects.none()
        self.fields['affected_device'].queryset = AffectedDevice.objects.none()
        self.fields['floor'].queryset = Floor.objects.none()

        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['sub_category'].queryset = SubCategory.objects.filter(category_id=category_id).order_by('name')
            except (ValueError, TypeError):
                pass  # Invalid input; ignore

        if 'sub_category' in self.data:
            try:
                sub_category_id = int(self.data.get('sub_category'))
                self.fields['issue'].queryset = Issue.objects.filter(sub_category_id=sub_category_id).order_by('name')
            except (ValueError, TypeError):
                pass  # Invalid input; ignore

        if 'issue' in self.data:
            try:
                issue_id = int(self.data.get('issue'))
                self.fields['affected_device'].queryset = AffectedDevice.objects.filter(issue_id=issue_id).order_by('name')
            except (ValueError, TypeError):
                pass  # Invalid input; ignore

        if 'building' in self.data:
            try:
                building_id = int(self.data.get('building'))
                self.fields['floor'].queryset = Floor.objects.filter(building_id=building_id).order_by('name')
            except (ValueError, TypeError):
                pass  # Invalid input; ignore

    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')
        allowed_extensions = ['pdf', 'csv', 'jpeg', 'jpg', 'png', 'xlsx']
        
        if attachment:
            # Check file size (5MB limit)
            if attachment.size > 5 * 1024 * 1024:
                raise ValidationError("The file size should not exceed 5MB.")

            # Check file extension
            ext = os.path.splitext(attachment.name)[1][1:].lower()  # Get the file extension without the dot
            if ext not in allowed_extensions:
                raise ValidationError("Only PDF, CSV, JPEG, JPG, PNG, and XLSX files are allowed.")
        
        return attachment