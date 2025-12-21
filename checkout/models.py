# checkout/models.py
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from cart.models import Cart
from products.models import Product, ProductBasket
from datetime import time


class DeliveryZone(models.Model):
    name = models.CharField(max_length=100, unique=True)
    delivery_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text="Delivery fee in KES (0 = free delivery)"
    )
    is_active = models.BooleanField(default=True, help_text="Uncheck to hide from checkout")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Delivery Zone"
        verbose_name_plural = "Delivery Zones"

    def __str__(self):
        return f"{self.name} (+KSh {self.delivery_fee})"


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=15)  # Normalized to 254...
    email = models.EmailField()
    zone = models.ForeignKey(
        DeliveryZone,
        on_delete=models.PROTECT,
        limit_choices_to={'is_active': True}
    )

    # Amounts
    subtotal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    checkout_request_id = models.CharField(max_length=100, blank=True, null=True)
    mpesa_receipt_number = models.CharField(max_length=50, blank=True, null=True)

    preferred_delivery_date = models.DateField(null=True, blank=True)
    preferred_delivery_time_start = models.TimeField(null=True, blank=True)
    preferred_delivery_time_end = models.TimeField(null=True, blank=True)

    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('paid', 'Paid'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Payment Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.get_full_name() or self.user.username} - {self.status}"

    @property
    def items(self):
        return self.order_items.all()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    basket = models.ForeignKey(ProductBasket, null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        if self.product:
            return f"{self.quantity} × {self.product.name}"
        return f"{self.quantity} × {self.basket.name} (Combo)"