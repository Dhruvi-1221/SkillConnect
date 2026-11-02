from django import forms
from .models import Order


class OrderBookingForm(forms.ModelForm):
    preferred_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'date'})
    )

    class Meta:
        model = Order
        fields = ['requirements', 'preferred_date', 'additional_message']
        widgets = {
            'requirements': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Explain your requirements clearly (e.g. date of photoshoot, design dimensions, specific colors, reference ideas, etc.)...'
            }),
            'additional_message': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 2,
                'placeholder': 'Any extra message or question for the student...'
            }),
        }
