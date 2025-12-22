from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
# REMOVE THIS LINE: from checkout.models import DeliveryZone 

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    county = models.CharField(max_length=100, blank=True, null=True)
    
    # FIX: Use string 'checkout.DeliveryZone' instead of the class directly
    zone = models.ForeignKey(
        'checkout.DeliveryZone',  # <--- This breaks the circular loop
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='users'
    )
    
    # System-managed fields
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Google auth field
    google_id = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.email

class EmailVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)