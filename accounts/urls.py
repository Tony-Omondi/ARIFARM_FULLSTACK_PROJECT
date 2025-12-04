# accounts/urls.py
from django.urls import path
from . import views
from .views import (
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView,
)

urlpatterns = [
    path('register/email/', views.email_register, name='email_register'),
    path('login/', views.user_login, name='login'),  # Customer login
    path('admin/login/', views.admin_login, name='admin_login'),  # Admin login
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('verification-sent/', views.email_verification_sent, name='email_verification_sent'),
    path('email-verified/', views.email_verified, name='email_verified'),
    # Password Reset Flow
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]