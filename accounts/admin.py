from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, EmailVerification


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = (
        'username', 'email', 'user_type', 'phone_number', 'is_verified',
        'is_active', 'last_login', 'date_joined'
    )
    list_filter = ('user_type', 'is_active', 'is_verified', 'is_staff')
    
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {
            'fields': (
                'first_name', 'last_name', 'phone_number', 'profile_picture',
                'county', 'zone', 'address'
            )
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'is_verified',
                'groups', 'user_permissions'
            )
        }),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
        ('Social Login', {'fields': ('google_id',)}),
        ('User Type', {'fields': ('user_type',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'user_type', 'password1', 'password2',
                'is_active', 'is_staff'
            ),
        }),
    )

    search_fields = ('email', 'username', 'phone_number')
    ordering = ('date_joined',)


admin.site.register(User, CustomUserAdmin)
admin.site.register(EmailVerification)
