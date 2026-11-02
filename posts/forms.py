from django import forms
from .models import Post, Comment
from accounts.models import Category


class PostForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Post
        fields = ['image', 'category', 'caption', 'skill_tags']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-file-input', 'accept': 'image/*'}),
            'caption': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Share the story behind this work, event, or design...'
            }),
            'skill_tags': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. Portrait, Lightroom, Festive (comma separated)'
            }),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'comment-input',
                'placeholder': 'Add a comment...',
                'autocomplete': 'off'
            })
        }
