from django.shortcuts import render, redirect, get_object_or_404
from store.models import product
from .models import Cart, CartItem
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.

# Private function
def _cart_id(request):
    cart = request.session.session_key
    if not cart: 
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    # Get the product
    products = product.objects.get(id = product_id) 
    # If the session key exists in the database, it only attributes another product to it
    try:
        # Get the cart using the _cart_id function
        cart = Cart.objects.get(cart_id = _cart_id(request)) 
    # If the session key doesn't exist in the database, then it creates a new one
    except Cart.DoesNotExist as e:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
    cart.save()

    # Putting the product inside the cart
    try:
        cart_item = CartItem.objects.get(product = products, cart = cart)
        # Incrementating the number of items whenever we add a product to cart 
        cart_item.quantity += 1     
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product = products,
            quantity = 1,
            cart = cart
        )
        cart_item.save()
    return redirect('cart')

def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id = _cart_id(request))
    products = get_object_or_404(product, id = product_id)
    cart_item = CartItem.objects.get(product = products, cart = cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

def delete_cart(request, product_id):
    cart = Cart.objects.get(cart_id = _cart_id(request))
    products = get_object_or_404(product, id = product_id)
    cart_item = CartItem.objects.get(product = products, cart = cart)
    cart_item.delete()
    return redirect('cart')

def cart(request, total = 0, quantity = 0, cart_items = None):
    try:
        tax = 0
        grand_total = 0
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_items = CartItem.objects.filter(cart = cart, is_active = True)
        for cart_item in cart_items:
            total += (cart_item.product.price*cart_item.quantity)
            quantity += cart_item.quantity
        tax = (0.08 * total)
        grand_total = total - tax
    except ObjectDoesNotExist :
        # ignoring
        pass 

    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
        'tax': tax,
        'grand_total': grand_total
    }

    return render(request, 'store/cart.html', context)

