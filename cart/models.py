# cart/models.py
from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product, ProductBasket, Merchandise  # Added Merchandise

User = get_user_model()


class Cart(models.Model):
    """One cart per registered user"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'

    def __str__(self):
        return f"Cart of {self.user.get_full_name() or self.user.username}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def item_count(self):
        return self.items.count()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')

    product = models.ForeignKey(
        Product,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    basket = models.ForeignKey(
        ProductBasket,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    merchandise = models.ForeignKey(
        Merchandise,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    # Exactly one of product, basket, or merchandise must be set
                    (models.Q(product__isnull=False, basket__isnull=True, merchandise__isnull=True)) |
                    (models.Q(product__isnull=True, basket__isnull=False, merchandise__isnull=True)) |
                    (models.Q(product__isnull=True, basket__isnull=True, merchandise__isnull=False))
                ),
                name='cartitem_exactly_one_item_type'
            )
        ]
        unique_together = ('cart', 'product', 'basket', 'merchandise')

    def __str__(self):
        if self.product:
            return f"{self.quantity} × {self.product.name}"
        if self.basket:
            return f"{self.quantity} × {self.basket.name} (Basket)"
        if self.merchandise:
            return f"{self.quantity} × {self.merchandise.name} (Merch)"
        return "Empty cart item"

    @property
    def unit_price(self):
        if self.product:
            return self.product.price
        elif self.basket:
            return self.basket.price
        elif self.merchandise:
            return self.merchandise.price
        return 0

    @property
    def total_price(self):
        return self.unit_price * self.quantity

    @property
    def name(self):
        if self.product:
            return self.product.name
        if self.basket:
            return self.basket.name
        if self.merchandise:
            return self.merchandise.name
        return "Unknown Item"

    @property
    def image(self):
        if self.product and self.product.image:
            return self.product.image.url
        if self.basket and self.basket.image:
            return self.basket.image.url
        if self.merchandise and self.merchandise.image:
            return self.merchandise.image.url
        return None