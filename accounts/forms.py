from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Profile, StudentProfile, CustomerProfile, Category, Skill

User = get_user_model()


class UserRegistrationForm(forms.ModelForm):
    ROLE_CHOICES = (
        ('CUSTOMER', 'I want to hire / find student services (Customer)'),
        ('STUDENT', 'I want to offer my skills and services (Student)'),
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'role-radio'}),
        initial='CUSTOMER'
    )
    full_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Aarav Patel'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'your.email@example.com'})
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Choose a username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Create strong password'}),
        min_length=6
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirm password'}),
        min_length=6
    )

    # Student specific fields
    college_name = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Pandit Deendayal Energy University (PDEU)'})
    )
    college_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'e.g. rollno@pdpu.ac.in'})
    )
    student_id = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'College Roll / ID Number'})
    )
    course = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. B.Tech Computer Engineering, B.Des, B.Com'})
    )
    year_of_study = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 2nd Year, 3rd Year, Final Year'})
    )
    college_id_card = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-file-input', 'accept': 'image/*'})
    )

    class Meta:
        model = User
        fields = ['full_name', 'username', 'email', 'role', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        role = cleaned_data.get('role')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        if role == 'STUDENT':
            college_name = cleaned_data.get('college_name')
            course = cleaned_data.get('course')
            year_of_study = cleaned_data.get('year_of_study')
            if not college_name:
                self.add_error('college_name', "College name is required for student registration.")
            if not course:
                self.add_error('course', "Course/Program is required for student registration.")
            if not year_of_study:
                self.add_error('year_of_study', "Year of study is required for student registration.")

        return cleaned_data


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username or Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password'}))

    def clean(self):
        username_or_email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username_or_email and password:
            user_by_email = User.objects.filter(email__iexact=username_or_email).first()
            auth_username = user_by_email.username if user_by_email else username_or_email

            from django.contrib.auth import authenticate
            self.user_cache = authenticate(self.request, username=auth_username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Invalid username/email or password. Please try again.")
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-input'})
    )

    class Meta:
        model = Profile
        fields = ['phone', 'bio', 'profile_picture', 'interests']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+91 9876543210'}),
            'bio': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Tell the community about yourself...'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-file-input', 'accept': 'image/*'}),
            'interests': forms.CheckboxSelectMultiple(attrs={'class': 'category-checkbox-grid'}),
        }


class StudentProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['college_name', 'college_email', 'student_id', 'course', 'year_of_study', 'is_available', 'skills']
        widgets = {
            'college_name': forms.TextInput(attrs={'class': 'form-input'}),
            'college_email': forms.EmailInput(attrs={'class': 'form-input'}),
            'student_id': forms.TextInput(attrs={'class': 'form-input'}),
            'course': forms.TextInput(attrs={'class': 'form-input'}),
            'year_of_study': forms.TextInput(attrs={'class': 'form-input'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'toggle-checkbox'}),
            'skills': forms.CheckboxSelectMultiple(attrs={'class': 'skill-checkbox-grid'}),
        }


class VerificationSubmissionForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['college_name', 'college_email', 'student_id', 'course', 'year_of_study', 'college_id_card']
        widgets = {
            'college_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Official College/University name'}),
            'college_email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Your student email (.ac.in / .edu)'}),
            'student_id': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Student Roll / Enrollment No.'}),
            'course': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Degree or Department'}),
            'year_of_study': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 1st Year, 2nd Year, 3rd Year, Final Year'}),
            'college_id_card': forms.FileInput(attrs={'class': 'form-file-input', 'accept': 'image/*'}),
        }
