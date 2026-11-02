from django import forms
from .models import Service
from accounts.models import Category


class ServiceForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Service
        fields = ['title', 'category', 'description', 'price', 'delivery_time_days', 'image', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Birthday Photography Session'}),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Explain what is included, what the customer should provide, and your process...'
            }),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '₹ Amount', 'step': '1', 'min': '0'}),
            'delivery_time_days': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Days', 'min': '1'}),
            'image': forms.FileInput(attrs={'class': 'form-file-input', 'accept': 'image/*'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'toggle-checkbox'}),
        }
