from django.contrib import admin
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0  # Prevents empty extra rows
    readonly_fields = ('total_price',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'item_count', 'total_price', 'created_at')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    inlines = [CartItemInline]

    # Added to show property fields in the list view
    def total_price(self, obj):
        return obj.total_price
    total_price.short_description = 'Total Price'

    def item_count(self, obj):
        return obj.item_count
    item_count.short_description = 'Unique Items'