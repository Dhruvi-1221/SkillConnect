from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=Review.RATING_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial=5
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Write your honest review about the student provider (e.g. quality, punctuality, communication)...'
            }),
        }
