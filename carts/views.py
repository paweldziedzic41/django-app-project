from django.shortcuts import render, redirect, get_object_or_404
from store.models import product, Variation
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
    # Storing the variation of the product in a list
    products_variation = []

    if request.method == 'POST':
        for item in request.POST:
            key = item
            # In the value variable are stored all informations
            value = request.POST[key]
            try:
                # __iexact formula will ignore if the key or value is lower or caps letter
                variation = Variation.objects.get(product = products, variation_category__iexact = key, variation_value__iexact = value)  
                products_variation.append(variation)
            except:
                pass
        
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

    # Checking if a cart item exists with certain variations
    is_cart_item_exist = CartItem.objects.filter(product = products, cart = cart).exists()
    # Putting the product inside the cart
    if is_cart_item_exist == True:
        cart_item = CartItem.objects.filter(product = products, cart = cart)
      
        ex_var_list = []
        id = [] 
        for item in cart_item:
            existing_variation = item.variations.all()
            ex_var_list.append(list(existing_variation))
            id.append(item.id)
        
        if products_variation in ex_var_list:
            # Increase quantity
            index = ex_var_list.index(products_variation)
            item_id = id[index]
            item = CartItem.objects.get(product = products, id = item_id)
            item.quantity += 1
            item.save()
        else:
            cart_item = CartItem.objects.create(product = products, quantity = 1, cart = cart)
            if len(products_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*products_variation)
            cart_item.save()
    else:
        cart_item = CartItem.objects.create(
            product = products,
            quantity = 1,
            cart = cart
        )
        if len(products_variation) > 0:
            cart_item.variations.clear()
            cart_item.variations.add(*products_variation)
        cart_item.save()
    return redirect('cart')


def remove_cart(request, product_id, cart_items_id):
    cart = Cart.objects.get(cart_id = _cart_id(request))
    products = get_object_or_404(product, id = product_id)
    try:
        cart_item = CartItem.objects.get(product = products, cart = cart , id = cart_items_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def delete_cart(request, product_id, cart_items_id):
    cart = Cart.objects.get(cart_id = _cart_id(request))
    products = get_object_or_404(product, id = product_id)
    cart_item = CartItem.objects.get(product = products, cart = cart, id = cart_items_id)
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

