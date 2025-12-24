# cart/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from products.models import Product, ProductBasket, Merchandise
from .models import Cart, CartItem


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
    """Add a product, basket, or merchandise to the user's cart."""
    cart, created = Cart.objects.get_or_create(user=request.user)

    product_id = request.POST.get('product_id')
    basket_id = request.POST.get('basket_id')
    merchandise_id = request.POST.get('merchandise_id')
    quantity = int(request.POST.get('quantity', 1))
    next_url = request.POST.get('next', 'products:product_list')

    if not (product_id or basket_id or merchandise_id):
        messages.error(request, "No item was selected.")
        return redirect(next_url)

    item = None
    item_name = ""
    item_type = ""

    if product_id:
        item = get_object_or_404(Product, id=product_id, is_active=True)
        item_name = item.name
        item_type = "product"

    elif basket_id:
        item = get_object_or_404(ProductBasket, id=basket_id, is_active=True)
        item_name = item.name
        item_type = "basket"

    elif merchandise_id:
        item = get_object_or_404(Merchandise, id=merchandise_id, is_active=True)
        item_name = item.name
        item_type = "merchandise"

    if item is None:
        messages.error(request, "Item not found or no longer available.")
        return redirect(next_url)

    # Stock check
    if item.stock < quantity:
        messages.error(request, f"Only {item.stock} {item_name}(s) left in stock.")
        return redirect(next_url)

    # Create or update CartItem
    defaults = {'quantity': quantity}

    if item_type == "product":
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=item, defaults=defaults
        )
    elif item_type == "basket":
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, basket=item, defaults=defaults
        )
    elif item_type == "merchandise":
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, merchandise=item, defaults=defaults
        )

    if not created:
        new_quantity = cart_item.quantity + quantity
        if item.stock < new_quantity:
            messages.error(request, f"Cannot add more – only {item.stock} in stock.")
            return redirect(next_url)
        cart_item.quantity = new_quantity
        cart_item.save()
        messages.success(request, f"Updated quantity of {item_name} in cart.")
    else:
        messages.success(request, f"{item_name} added to cart!")

    return redirect('cart:cart_detail')


@require_POST
@login_required
def update_cart_item(request):
    """Update quantity of a cart item or remove if quantity <= 0."""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item_id = request.POST.get('item_id')
    quantity = int(request.POST.get('quantity', 0))

    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

    # Determine name and stock
    if cart_item.product:
        item_name = cart_item.product.name
        stock = cart_item.product.stock
    elif cart_item.basket:
        item_name = cart_item.basket.name
        stock = cart_item.basket.stock
    elif cart_item.merchandise:
        item_name = cart_item.merchandise.name
        stock = cart_item.merchandise.stock
    else:
        item_name = "Unknown item"
        stock = 0

    if quantity <= 0:
        cart_item.delete()
        messages.info(request, f"{item_name} removed from cart.")
    else:
        if stock < quantity:
            messages.error(request, f"Only {stock} in stock.")
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, "Cart updated successfully.")

    return redirect('cart:cart_detail')


@login_required
def remove_from_cart(request, item_id):
    """Remove a specific item from the cart."""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

    item_name = (
        cart_item.product.name if cart_item.product else
        cart_item.basket.name if cart_item.basket else
        cart_item.merchandise.name if cart_item.merchandise else
        "Item"
    )

    cart_item.delete()
    messages.success(request, f"{item_name} removed from cart.")
    return redirect('cart:cart_detail')


@login_required
def clear_cart(request):
    """Remove all items from the user's cart."""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart.items.all().delete()
    messages.success(request, "Your cart has been cleared.")
    return redirect('cart:cart_detail')