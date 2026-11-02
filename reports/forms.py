from django import forms
from .models import Report


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['target_type', 'target_id', 'reason', 'details']
        widgets = {
            'target_type': forms.HiddenInput(),
            'target_id': forms.HiddenInput(),
            'reason': forms.Select(attrs={'class': 'form-select'}),
            'details': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Please provide details describing what violation occurred...'
            }),
        }
