# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import uuid
from .forms import EmailRegistrationForm, ProfileUpdateForm
from .models import User, EmailVerification

def email_register(request):
    if request.user.is_authenticated:
        return redirect('profile')
        
    if request.method == 'POST':
        form = EmailRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email']  # Use email as username
            user.is_verified = False
            user.user_type = 'customer'  # Set as customer
            user.save()
            
            # Create verification token
            token = str(uuid.uuid4())
            EmailVerification.objects.create(user=user, token=token)
            
            # Send verification email
            verification_url = f"{settings.SITE_URL}/accounts/verify-email/{token}/"
            send_mail(
                'Verify your email address',
                f'Click here to verify your email: {verification_url}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            return redirect('email_verification_sent')
    else:
        form = EmailRegistrationForm()
    
    return render(request, 'accounts/email_register.html', {'form': form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if user.user_type == 'customer' or user.user_type == 'admin':
                login(request, user)
                messages.success(request, 'Login successful!')
                return redirect('profile')
            else:
                messages.error(request, 'Invalid user type')
        else:
            messages.error(request, 'Invalid email or password')
    
    return render(request, 'accounts/login.html')

def admin_login(request):
    if request.user.is_authenticated and request.user.user_type == 'admin':
        return redirect('/admin/')  # Redirect to Django admin
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None and user.user_type == 'admin':
            login(request, user)
            messages.success(request, 'Admin login successful!')
            return redirect('/admin/')  # Redirect to Django admin dashboard
        else:
            messages.error(request, 'Invalid admin credentials')
    
    return render(request, 'accounts/admin_login.html')

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

def verify_email(request, token):
    try:
        verification = EmailVerification.objects.get(token=token, is_used=False)
        user = verification.user
        user.is_verified = True
        user.save()
        
        verification.is_used = True
        verification.save()
        
        messages.success(request, 'Email verified successfully! You can now login.')
        return redirect('email_verified')
    except EmailVerification.DoesNotExist:
        messages.error(request, 'Invalid or expired verification link.')
        return render(request, 'accounts/verification_invalid.html')

def email_verification_sent(request):
    return render(request, 'accounts/email_verification_sent.html')

def email_verified(request):
    return render(request, 'accounts/email_verified.html')

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})