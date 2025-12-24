from django.contrib import admin
from django.utils.html import format_html
from .models import DeliveryZone, Order, OrderItem

# --- UNFOLD IMPORTS ---
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
# ----------------------

@admin.register(DeliveryZone)
class DeliveryZoneAdmin(ModelAdmin):
    list_display = ('name', 'fee_display', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('name',)
    list_editable = ('is_active',)

    @display(description="Delivery Fee")
    def fee_display(self, obj):
        # Safety check for None
        if obj.delivery_fee is None:
            return "-"
        if obj.delivery_fee == 0:
            return "Free"
        return f"KSh {obj.delivery_fee:,.2f}"


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    # We display these as read-only columns
    readonly_fields = ('product_info', 'quantity', 'unit_price_display', 'total_price_display')
    fields = ('product_info', 'quantity', 'unit_price_display', 'total_price_display')
    can_delete = False
    
    @display(description="Item")
    def product_info(self, obj):
        # Check if obj exists (it might be None for an empty extra row)
        if not obj or not obj.pk:
            return "-"
            
        if obj.product:
            return obj.product.name
        elif obj.basket:
            return f"{obj.basket.name} (Combo)"
        return "Unknown Item"

    @display(description="Unit Price")
    def unit_price_display(self, obj):
        # FIX: Check for None to prevent TypeError
        if obj.unit_price is None:
            return "-"
        return f"KSh {obj.unit_price:,.2f}"

    @display(description="Total")
    def total_price_display(self, obj):
        # FIX: Check for None to prevent TypeError
        if obj.total_price is None:
            return "-"
        return f"KSh {obj.total_price:,.2f}"


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = (
        'order_id_display',
        'customer_info',
        'phone_number',
        'zone',
        'total_amount_display',
        'status_badge',
        'created_at',
    )
    list_filter = ('status', 'zone', 'created_at')
    search_fields = ('id', 'user__username', 'user__email', 'phone_number', 'mpesa_receipt_number')
    inlines = [OrderItemInline]
    ordering = ('-created_at',)
    list_per_page = 20

    fieldsets = (
        ('Order Status', {
            'fields': ('status', 'created_at')
        }),
        ('Customer Details', {
            'fields': ('user', 'phone_number', 'email', 'zone', 'preferred_delivery_date', 'preferred_delivery_time_start', 'preferred_delivery_time_end'),
            'classes': ('tab',),
        }),
        ('Payment Information', {
            'fields': ('subtotal_amount', 'delivery_fee', 'total_amount', 'mpesa_receipt_number', 'checkout_request_id'),
            'classes': ('tab',),
        }),
    )

    readonly_fields = (
        'subtotal_amount', 'delivery_fee', 'total_amount', 
        'checkout_request_id', 'mpesa_receipt_number', 
        'created_at', 'updated_at'
    )

    @display(description="Order #", ordering="id")
    def order_id_display(self, obj):
        return f"#{obj.id}"

    @display(description="Customer")
    def customer_info(self, obj):
        if not obj.user:
            return "Guest"
        return obj.user.get_full_name() or obj.user.username

    @display(description="Total")
    def total_amount_display(self, obj):
        if obj.total_amount is None:
            return "-"
        return f"KSh {obj.total_amount:,.2f}"

    @display(
        description="Status",
        label={
            'pending': 'warning',          # Yellow
            'processing': 'info',          # Light Blue
            'paid': 'info',                # Light Blue
            'confirmed': 'primary',        # Greenish/Primary
            'out_for_delivery': 'primary', # Greenish
            'delivered': 'success',        # Green
            'cancelled': 'danger',         # Red
            'failed': 'danger',            # Red
        }
    )
    def status_badge(self, obj):
        return obj.get_status_display()