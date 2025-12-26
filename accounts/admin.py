from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.decorators import display

from .models import User, EmailVerification

# ================= HELPER FUNCTIONS =================

def display_image(image_field):
    """Helper to display small thumbnails in admin list"""
    if image_field:
        return format_html(
            '<img src="{}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 50%;" />',
            image_field.url
        )
    return format_html('<span style="color: #ccc;">-</span>')


# ================= ADMIN CLASSES =================

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin, ModelAdmin):
    # Inherit from BaseUserAdmin first to keep password management, 
    # and ModelAdmin second to get Unfold styles.
    
    list_display = [
        'image_preview', 'username', 'email', 'user_type_badge', 
        'phone_number', 'verification_status', 'status_badge', 
        'date_joined', 'last_login'
    ]
    list_filter = ['user_type', 'is_active', 'is_verified', 'is_staff']
    search_fields = ['username', 'email', 'phone_number']
    ordering = ('-date_joined',)
    
    # Organize fields using Unfold classes (tabs, colors)
    fieldsets = (
        ('Account Credentials', {
            'fields': (('username', 'email'), 'password')
        }),
        ('Personal Information', {
            'classes': ('tab',),
            'fields': (
                ('first_name', 'last_name'),
                'profile_picture',
                'phone_number',
            )
        }),
        ('Location Details', {
            'classes': ('tab',),
            'fields': (
                ('county', 'zone'),
                'address'
            )
        }),
        ('Permissions & Status', {
            'classes': ('bg-gray-50', 'border', 'border-gray-200', 'rounded-md', 'p-4'),
            'fields': (
                ('is_active', 'is_staff', 'is_superuser'),
                ('is_verified', 'user_type'),
                'groups', 
                'user_permissions'
            )
        }),
        ('Metadata', {
            'classes': ('collapse',),
            'fields': ('last_login', 'date_joined', 'google_id')
        }),
    )

    # Decorators for visual enhancements
    @display(description="Avatar")
    def image_preview(self, obj):
        return display_image(obj.profile_picture)

    @display(
        description="Status",
        label={
            True: "success",  # Green
            False: "danger"   # Red
        }
    )
    def status_badge(self, obj):
        return obj.is_active

    @display(
        description="Verified",
        label={
            True: "success", 
            False: "warning"  # Yellow for unverified
        }
    )
    def verification_status(self, obj):
        return obj.is_verified

    @display(
        description="Type",
        label={
            # Adjust these keys based on your actual User Type choices
            "admin": "primary",    # Purple/Blue
            "customer": "info",    # Light Blue
            "vendor": "warning",   # Orange/Yellow
            "staff": "secondary",  # Gray
        }
    )
    def user_type_badge(self, obj):
        return obj.user_type


@admin.register(EmailVerification)
class EmailVerificationAdmin(ModelAdmin):
    list_display = ['user', 'code_preview', 'created_at', 'expires_at_display']
    search_fields = ['user__email', 'user__username', 'code']
    readonly_fields = ['created_at']
    list_filter = ['created_at']

    @display(description="Code")
    def code_preview(self, obj):
        # Obfuscate code for security in list view
        if obj.code:
            return f"{obj.code[:4]}..."
        return "-"

    @display(description="Expires At")
    def expires_at_display(self, obj):
        # Example: You might calculate expiry based on created_at logic here
        # or display a field if it exists. Assuming standard timestamp:
        return f"{obj.created_at}"