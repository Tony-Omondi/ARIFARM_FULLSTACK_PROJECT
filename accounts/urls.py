# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('register/email/', views.email_register, name='email_register'),
    path('login/', views.user_login, name='login'),  # Customer login
    path('admin/login/', views.admin_login, name='admin_login'),  # Admin login
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('verification-sent/', views.email_verification_sent, name='email_verification_sent'),
    path('email-verified/', views.email_verified, name='email_verified'),
]