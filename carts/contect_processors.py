from .models import Cart, CartItem
from .views import _cart_id

def counter(request):
    cart_count = 0
    if 'admin' in request.path:
        return ()
    else:
        try:
            cart = Cart.objects.filter(cart_id = _cart_id(request))
            # When the user is logged
            if request.user.is_authenticated:
                cart_item = CartItem.objects.all().filter(user = request.user)
            # When the user isn't logged
            else:
                cart_item = CartItem.objects.all().filter(cart = cart[:1])
            for cart_items in cart_item:
                cart_count += cart_items.quantity
        except Cart.DoesNotExist:
            cart_count = 0
    return dict(cart_count = cart_count)
