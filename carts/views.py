from django.shortcuts import render, redirect, get_object_or_404
from store.models import product, Variation
from .models import Cart, CartItem
from accounts.models import Account
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.db.models import Q
# Create your views here.

# Private function
def _cart_id(request):
    cart = request.session.session_key
    if not cart: 
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    if request.user.is_authenticated:
        current_user = request.user
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
        
        # Checking if a cart item exists with certain variations
        is_cart_item_exist = CartItem.objects.filter(product = products, user = current_user).exists()
        # Putting the product inside the cart
        if is_cart_item_exist == True:
            cart_item = CartItem.objects.filter(product = products, user = current_user)
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
                cart_item = CartItem.objects.create(product = products, quantity = 1, user = current_user)
                cart_item.cart = None
                if len(products_variation) > 0:
                    cart_item.variations.clear()
                    cart_item.variations.add(*products_variation)
                cart_item.save()
        else:
            cart_item = CartItem.objects.create(
                product = products,
                quantity = 1,
                user = current_user
                )
            if len(products_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*products_variation)
            cart_item.save()
        return redirect('cart')
    else:
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
                cart = Cart.objects.create(cart_id = _cart_id(request))
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


def remove_cart(request, cart_items_id):
        try:
            cart_item = CartItem.objects.get(id = cart_items_id)
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
        except:
            pass
        return redirect('cart')

def delete_cart(request, cart_items_id):
    cart_item = CartItem.objects.get(id = cart_items_id)
    cart_item.delete()
    return redirect('cart')

def cart(request, total = 0, quantity = 0, cart_items = None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.all().filter(user = request.user)
        else:
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

@login_required(login_url='login')
def checkout(request, total = 0, quantity = 0):
    try:
        tax = 0
        grand_total = 0
        cart_items = CartItem.objects.filter(user = request.user, is_active = True)
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
    return render(request, 'store/checkout.html', context)

def change_cart_items_when_logged(session_cart_items, user, cart):
    L_session_prod = []
    L_var_session_prod = []
    for item in session_cart_items:
        session_cart_item = item.product
        var_session_prod = item.variations.all()
        L_session_prod.append(session_cart_item)
        L_var_session_prod.append(list(var_session_prod))
    user_cart_items = CartItem.objects.filter(user = user)
    L_user_prod = []
    for item in user_cart_items:
        user_cart_item = item.product
        L_user_prod.append(user_cart_item)
    for index, session_item in enumerate(L_session_prod):
        var_color = L_var_session_prod[index][0]
        var_size = L_var_session_prod[index][1]
        session_cart_item = CartItem.objects.filter(variations__variation_value = var_color, product = session_item,
                                                        user = None, cart = cart
                                                        ).filter(variations__variation_value = var_size)
        session_cart_item = session_cart_item.get()
        if session_item in L_user_prod:
            # List of variations of user products
            ex_var_list_user = []
            user_cart_item = CartItem.objects.filter(product = session_item)
            for user_item in user_cart_item:
                ex_var_list_user.append(list(user_item.variations.all()))
            for var_session_item in L_var_session_prod:
                # User cart has an identical item in session cart
                if var_session_item == ex_var_list_user[index]:
                    user_cart_item = CartItem.objects.filter(variations__variation_value = var_color, product = session_item,
                                                                user = user, cart = None
                                                                ).filter(variations__variation_value = var_size)
                    user_cart_item = user_cart_item.get()
                    user_cart_item.quantity += session_cart_item.quantity
                    session_cart_item.delete()
                    user_cart_item.save()
                # User cart has an identical item in the session cart but in antoher variation
                else:
                    session_cart_item.user = user
                    session_cart_item.cart = None
                    session_cart_item.save()
        # User cart dosent have identical item in the session cart
        else:
             session_cart_item.cart = None
             session_cart_item.user = user
             session_cart_item.save()


    