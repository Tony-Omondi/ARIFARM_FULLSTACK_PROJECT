# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from checkout.models import DeliveryZone  # <--- Import DeliveryZone model

class EmailRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address'
        })
    )
    
    class Meta:
        model = User
        fields = ['email', 'password1', 'password2'] 
        widgets = {
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Password'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Confirm Password'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class ProfileUpdateForm(forms.ModelForm):
    # Explicitly define zone as a ModelChoiceField to create a dropdown fetching from DB
    zone = forms.ModelChoiceField(
        queryset=DeliveryZone.objects.filter(is_active=True), # Only get active zones
        empty_label="Select your Delivery Zone",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = User
        # Removed 'address' from fields
        fields = ['first_name', 'last_name', 'phone_number', 'profile_picture', 'county', 'zone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            # Note: We don't need a widget for 'county' because you hardcoded the <select> in HTML,
            # but Django will still accept the data sent from it.
        }