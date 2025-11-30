# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class EmailRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ['email', 'password1', 'password2', 'confirm_password']
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password1")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        
        return cleaned_data

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'profile_picture', 'county', 'zone', 'address']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'county': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'County'}),
            'zone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Zone'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Address'}),
        }