from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('unit_price', 'total_price')
    # Make items read-only if you don't want admins changing order history
    # can_delete = False 

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'status', 'total_amount', 
        'mpesa_receipt_number', 'created_at'
    )
    list_filter = ('status', 'created_at', 'zone')
    search_fields = (
        'user__username', 'mpesa_receipt_number', 
        'checkout_request_id', 'phone_number'
    )
    ordering = ('-created_at',)
    inlines = [OrderItemInline]
    
    # Optional: Grouping fields in the detail view
    fieldsets = (
        ('Customer Info', {
            'fields': ('user', 'phone_number', 'email', 'zone')
        }),
        ('Payment Details', {
            'fields': ('total_amount', 'status', 'checkout_request_id', 'mpesa_receipt_number')
        }),
        ('Metadata', {
            'fields': ('cart', 'created_at', 'updated_at'),
            'classes': ('collapse',), # Hides this section by default
        }),
    )
    readonly_fields = ('created_at', 'updated_at')