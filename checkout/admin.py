from django.contrib import admin
from .models import DeliveryZone, Order, OrderItem


@admin.register(DeliveryZone)
class DeliveryZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'delivery_fee', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('name',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'basket', 'quantity', 'unit_price', 'total_price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'phone_number',
        'zone',
        'total_amount',
        'status',
        'created_at',
    )
    list_filter = ('status', 'zone', 'created_at')
    search_fields = ('id', 'user__username', 'phone_number', 'email')
    readonly_fields = (
        'subtotal_amount',
        'delivery_fee',
        'total_amount',
        'checkout_request_id',
        'mpesa_receipt_number',
        'created_at',
        'updated_at',
    )
    inlines = [OrderItemInline]
    ordering = ('-created_at',)
