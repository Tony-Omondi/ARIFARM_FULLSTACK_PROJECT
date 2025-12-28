from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string  # <--- NEW IMPORT
from django.utils.html import strip_tags             # <--- NEW IMPORT
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

            # Prepare Email Data
            verification_url = f"{settings.SITE_URL}/accounts/verify-email/{token}/"
            
            # Context for the HTML template
            context = {
                'user': user,
                'verification_url': verification_url,
            }

            # Render HTML content
            html_message = render_to_string('accounts/verification_email.html', context)
            
            # Create Plain Text fallback (strips HTML tags)
            plain_message = strip_tags(html_message)

            # Send Email (Both HTML and Plain Text)
            send_mail(
                subject='Verify Your Email - AriFarm Shop',
                message=plain_message,            # Fallback for old email clients
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,        # The beautiful HTML version
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
    
    return render(request, 'accounts/admin_login.html')


def verify_email(request, token):
    try:
        verification = EmailVerification.objects.get(token=token, is_used=False)
        user = verification.user
        
        # Activate and verify the user
        user.is_verified = True
        user.is_active = True  # Ensure user is active
        user.save()
        
        # Mark verification as used
        verification.is_used = True
        verification.save()

        # FIX: Set the backend explicitly before login to avoid "multiple authentication backends" error
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        
        # Auto-login after verification
        login(request, user)
        
        messages.success(request, 'Email verified successfully! You are now logged in.')
        return redirect('email_verified')
    
    except EmailVerification.DoesNotExist:
        messages.error(request, 'Invalid or expired verification link.')
        return render(request, 'accounts/verification_invalid.html')


def email_verification_sent(request):
    # Get email from session
    email = request.session.get('registered_email', '')
    return render(request, 'accounts/email_verification_sent.html', {'email': email})


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
    """
    User profile view with update form and dashboard statistics
    """
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    # Calculate order statistics for dashboard cards
    total_orders = request.user.orders.count()
    paid_orders = request.user.orders.filter(status='paid').count()          # typically "Processing / Pending Delivery"
    pending_orders = request.user.orders.filter(status='pending').count()    # Awaiting Payment/Confirmation

    # Optional additional stats (uncomment if you want to use them)
    # processing_orders = request.user.orders.filter(status='processing').count()
    # delivered_orders = request.user.orders.filter(status='delivered').count()
    # failed_orders = request.user.orders.filter(status__in=['failed', 'cancelled']).count()

    context = {
        'form': form,
        'total_orders': total_orders,
        'paid_orders': paid_orders,
        'pending_orders': pending_orders,
        # Add more if you decide to display them:
        # 'processing_orders': processing_orders,
        # 'delivered_orders': delivered_orders,
        # 'failed_orders': failed_orders,
    }

    return render(request, 'accounts/profile.html', context)


# =============================== PASSWORD RESET (FIXED + WORKING) ===============================
class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    
    # 1. Used for plain text version (Optional if you only care about HTML clients)
    email_template_name = 'accounts/password_reset_email.html' 
    
    # 2. ADD THIS: Django uses this attribute to send the HTML version
    html_email_template_name = 'accounts/password_reset_email.html' 
    
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
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        
        messages.success(self.request, 'Password changed successfully! You are now logged in.')
        return super().form_valid(form)


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'