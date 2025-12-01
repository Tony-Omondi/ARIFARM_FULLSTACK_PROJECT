from .models import Cart

def cart_context(request):
    """Make cart available in all templates"""
    context = {}
    
    if request.user.is_authenticated:
        # Get or create cart for logged-in user
        cart, created = Cart.objects.get_or_create(
            user=request.user,
            status='active',
            defaults={'session_key': request.session.session_key}
        )
        context['cart'] = cart
        context['cart_item_count'] = cart.get_item_count()
    else:
        # For guests, use session-based cart
        if not request.session.session_key:
            request.session.create()
        
        session_key = request.session.session_key
        try:
            cart = Cart.objects.get(session_key=session_key, status='active')
        except Cart.DoesNotExist:
            cart = Cart.objects.create(session_key=session_key, status='active')
        
        context['cart'] = cart
        context['cart_item_count'] = cart.get_item_count()
    
    return context