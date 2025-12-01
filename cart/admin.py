from django.contrib import admin
from .models import Cart, CartItem

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'item_count', 'total', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'delivery_name', 'delivery_phone')
    readonly_fields = ('created_at', 'updated_at')
    
    def item_count(self, obj):
        return obj.items.count()
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('items')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'item_type', 'name', 'quantity', 'price', 'total_price')
    list_filter = ('item_type', 'added_at')
    search_fields = ('cart__id', 'product__name', 'basket__name')
    
    def name(self, obj):
        return obj.name
    
    def total_price(self, obj):
        return obj.total_price
    total_price.admin_order_field = 'price'