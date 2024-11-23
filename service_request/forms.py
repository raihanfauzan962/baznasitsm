from django import forms
from typing import Any, Dict, List

class DynamicServiceRequestForm(forms.Form):
    def __init__(self, *args: Any, **kwargs: Dict[str, Any]):
        asset_form = kwargs.pop('asset_form')
        super().__init__(*args, **kwargs)

        # Dynamically create form fields from JSON
        self.create_dynamic_fields(asset_form['fields'])

    def create_dynamic_fields(self, fields: List[Dict[str, Any]]) -> None:
        for field in fields:
            field_type = field['type']
            field_name = field['name']
            required = field.get('required', False)
            label = field.get('label', '')
            help_text = field.get('help_text', '')

            # Create fields based on their type
            if field_type == 'text':
                self.fields[field_name] = forms.CharField(
                    label=label,
                    required=required,
                    widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': field.get('placeholder', '')}),
                    help_text=help_text
                )

            elif field_type == 'email':
                self.fields[field_name] = forms.EmailField(
                    label=label,
                    required=required,
                    widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': field.get('placeholder', '')}),
                    help_text=help_text
                )

            elif field_type == 'select':
                self.fields[field_name] = forms.ChoiceField(
                    label=label,
                    required=required,
                    choices=[(option['value'], option['label']) for option in field['options']],
                    widget=forms.Select(attrs={'class': 'form-select'}),
                    help_text=help_text
                )

            elif field_type == 'radio':
                self.fields[field_name] = forms.ChoiceField(
                    label=label,
                    required=required,
                    choices=[(option['value'], option['label']) for option in field['options']],
                    widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                    help_text=help_text
                )

            elif field_type == 'checkbox':
                self.fields[field_name] = forms.BooleanField(
                    required=required,
                    label=label,
                    widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
                    help_text=help_text
                )

            elif field_type == 'multiple_checkbox':
                self.fields[field_name] = forms.MultipleChoiceField(
                    label=label,
                    required=required,
                    choices=[(option['value'], option['label']) for option in field['options']],
                    widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check'}),
                    help_text=help_text
                )

            elif field_type == 'number':
                self.fields[field_name] = forms.IntegerField(
                    label=label,
                    required=required,
                    widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': field.get('placeholder', '')}),
                    help_text=help_text
                )

            elif field_type == 'textarea':
                self.fields[field_name] = forms.CharField(
                    label=label,
                    required=required,
                    widget=forms.Textarea(attrs={
                        'class': 'form-control',
                        'placeholder': field.get('placeholder', ''),
                        'rows': field.get('rows', 3)  # Default rows can be set to 3
                    }),
                    help_text=help_text
                )

            elif field_type == 'date':
                self.fields[field_name] = forms.DateField(
                    label=label,
                    required=required,
                    widget=forms.DateInput(attrs={
                        'class': 'form-control',
                        'placeholder': field.get('placeholder', ''),
                        'type': 'date'  # Use HTML5 date input
                    }),
                    help_text=help_text
                )

            # You can add more field types as needed...
