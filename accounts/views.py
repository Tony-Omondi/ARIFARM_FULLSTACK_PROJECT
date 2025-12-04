# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.urls import reverse_lazy
import uuid

from .forms import EmailRegistrationForm, ProfileUpdateForm
from .models import User, EmailVerification


# ========================== REGISTRATION & VERIFICATION ==========================
def email_register(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = EmailRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email']
            user.is_verified = False
            user.user_type = 'customer'
            user.save()

            # Generate verification token
            token = str(uuid.uuid4())
            EmailVerification.objects.create(user=user, token=token)

            # Send verification email (same as before)
            verification_url = f"{settings.SITE_URL}/accounts/verify-email/{token}/"
            send_mail(
                subject='Verify Your Email - Oreg Organic Shop',
                message=f'Hi {user.email},\n\nClick the link below to verify your account:\n\n{verification_url}\n\nThank you!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            # Save email in session so verification_sent page can show it
            request.session['registered_email'] = user.email
            return redirect('email_verification_sent')
    else:
        form = EmailRegistrationForm()

    return render(request, 'accounts/email_register.html', {'form': form})


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


def verify_email(request, token):
    try:
        verification = EmailVerification.objects.get(token=token, is_used=False)
        user = verification.user
        user.is_verified = True
        user.save()
        verification.is_used = True
        verification.save()

        messages.success(request, 'Email verified successfully! You can now login.')
        login(request, user)  # Auto-login after verification
        return redirect('email_verified')
    except EmailVerification.DoesNotExist:
        messages.error(request, 'Invalid or expired verification link.')
        return render(request, 'accounts/verification_invalid.html')


def email_verification_sent(request):
    return render(request, 'accounts/email_verification_sent.html')

def email_verified(request):
    return render(request, 'accounts/email_verified.html')


# =================================== LOGIN / LOGOUT ===================================
def user_login(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            if user.is_verified:
                login(request, user)
                next_url = request.GET.get('next', 'profile')
                return redirect(next_url)
            else:
                messages.error(request, 'Please verify your email first.')
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'accounts/login.html')


def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


# =================================== PROFILE ===================================
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


# =============================== PASSWORD RESET (FIXED + WORKING) ===============================
class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        messages.success(self.request, 'If your email exists, a reset link has been sent.')
        return super().form_valid(form)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

    def form_valid(self, form):
        # Save the new password
        user = form.save()
        
        # Manual login with explicit backend → FIXES THE MULTIPLE BACKENDS ERROR
        from django.contrib.auth import login
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        
        messages.success(self.request, 'Password changed successfully! You are now logged in.')
        return super().form_valid(form)


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'


# Optional: Remove admin_login if you don't want separate admin page
# def admin_login(request): ... → you can delete this entirely if not needed