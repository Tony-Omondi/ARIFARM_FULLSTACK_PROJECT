# cart/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from products.models import Product, ProductBasket
from .models import Cart, CartItem  # ← Added Cart import


@login_required
def cart_detail(request):
    """Display the user's cart. Creates cart if missing."""
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart/cart_detail.html', {
        'cart': cart,
    })


@require_POST
@login_required
def add_to_cart(request):
    """Add a product or basket to the user's cart."""
    # Safely get or create the cart
    cart, created = Cart.objects.get_or_create(user=request.user)

    product_id = request.POST.get('product_id')
    basket_id = request.POST.get('basket_id')
    quantity = int(request.POST.get('quantity', 1))
    next_url = request.POST.get('next', 'products:home')

    if not product_id and not basket_id:
        messages.error(request, "No item was selected.")
        return redirect(next_url)

    if product_id:
        product = get_object_or_404(Product, id=product_id, is_active=True)

        if product.stock < quantity:
            messages.error(request, f"Only {product.stock} {product.name}(s) left in stock.")
            return redirect(next_url)

        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not item_created:
            new_quantity = cart_item.quantity + quantity
            if product.stock < new_quantity:
                messages.error(request, f"Cannot add more – only {product.stock} in stock.")
                return redirect(next_url)
            cart_item.quantity = new_quantity
            cart_item.save()
            messages.success(request, f"Updated quantity of {product.name} in cart.")
        else:
            messages.success(request, f"{product.name} added to cart!")

    elif basket_id:
        basket = get_object_or_404(ProductBasket, id=basket_id, is_active=True)

        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            basket=basket,
            defaults={'quantity': quantity}
        )

        if not item_created:
            cart_item.quantity += quantity
            cart_item.save()
            messages.success(request, f"Updated quantity of {basket.name} basket in cart.")
        else:
            messages.success(request, f"{basket.name} basket added to cart!")

    return redirect('cart:cart_detail')


@require_POST
@login_required
def update_cart_item(request):
    """Update quantity of a cart item or remove if quantity <= 0."""
    cart, _ = Cart.objects.get_or_create(user=request.user)

    item_id = request.POST.get('item_id')
    quantity = int(request.POST.get('quantity', 0))

    item = get_object_or_404(CartItem, id=item_id, cart=cart)

    if quantity <= 0:
        item_name = item.product.name if item.product else item.basket.name
        item.delete()
        messages.info(request, f"{item_name} removed from cart.")
    else:
        if item.product and item.product.stock < quantity:
            messages.error(request, f"Only {item.product.stock} in stock.")
        else:
            item.quantity = quantity
            item.save()
            messages.success(request, "Cart updated successfully.")

    return redirect('cart:cart_detail')


@login_required
def remove_from_cart(request, item_id):
    """Remove a specific item from the cart."""
    cart, _ = Cart.objects.get_or_create(user=request.user)

    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item_name = item.product.name if item.product else item.basket.name
    item.delete()
    messages.success(request, f"{item_name} removed from cart.")
    return redirect('cart:cart_detail')


@login_required
def clear_cart(request):
    """Remove all items from the user's cart."""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart.items.all().delete()
    messages.success(request, "Your cart has been cleared.")
    return redirect('cart:cart_detail')