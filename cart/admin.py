from django.contrib import admin
from django.utils.html import format_html
from .models import Cart, CartItem

# --- UNFOLD IMPORTS ---
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
# ----------------------

class CartItemInline(TabularInline):
    model = CartItem
    extra = 0
    can_delete = True
    fields = ('image_preview', 'product_name', 'quantity', 'unit_price_display', 'total_price_display')
    readonly_fields = ('image_preview', 'product_name', 'unit_price_display', 'total_price_display')
    
    @display(description="Image")
    def image_preview(self, obj):
        # Safely get the image URL from the property you defined in models.py
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 6px;" />',
                obj.image
            )
        return "-"

    @display(description="Item Name")
    def product_name(self, obj):
        return obj.name

    @display(description="Unit Price")
    def unit_price_display(self, obj):
        return f"KSh {obj.unit_price:,.2f}"

    @display(description="Total Line Price")
    def total_price_display(self, obj):
        return f"KSh {obj.total_price:,.2f}"


@admin.register(Cart)
class CartAdmin(ModelAdmin):
    list_display = ('cart_id_display', 'user_info', 'items_badge', 'total_price_display', 'updated_at')
    search_fields = ('user__username', 'user__email', 'user__first_name')
    list_filter = ('created_at', 'updated_at')
    inlines = [CartItemInline]
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20

    @display(description="Cart ID", ordering="id")
    def cart_id_display(self, obj):
        return f"#{obj.id}"

    @display(description="Customer")
    def user_info(self, obj):
        return obj.user.get_full_name() or obj.user.username

    @display(description="Items", label=True) # Renders as a numbered badge
    def items_badge(self, obj):
        return obj.item_count

    @display(description="Total Value")
    def total_price_display(self, obj):
        return f"KSh {obj.total_price:,.2f}"