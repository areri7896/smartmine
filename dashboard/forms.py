from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Profile
from .constants import COUNTRY_CHOICES


class EmailUsersForm(forms.Form):
    subject = forms.CharField(max_length=255)
    message = forms.CharField(widget=forms.Textarea)


# Custom User Creation Form
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"}),
            'email': forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}),
            'first_name': forms.TextInput(attrs={"class": "form-control", "placeholder": "First Name"}),
            'last_name': forms.TextInput(attrs={"class": "form-control", "placeholder": "Last Name"}),
        }


# Custom User Change Form
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"}),
            'email': forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}),
            'first_name': forms.TextInput(attrs={"class": "form-control", "placeholder": "First Name"}),
            'last_name': forms.TextInput(attrs={"class": "form-control", "placeholder": "Last Name"}),
        }


# Profile Update Form
class ProfileUpdateForm(forms.ModelForm):
    # Using shared COUNTRY_CHOICES from constants.py
    country = forms.ChoiceField(
        choices=COUNTRY_CHOICES,
        required=True,
        label="Country",
    )

    class Meta:
        model = Profile
        fields = ['profile_pic', 'dob', 'country']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date', "placeholder": "Date of Birth", "class": "form-control"}),
            'profile_pic': forms.ClearableFileInput(attrs={"placeholder": "Profile Picture", "class": "form-control"}),
            'country': forms.Select(attrs={"class": "form-control"}),
        }