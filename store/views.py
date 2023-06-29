from django.shortcuts import render, get_object_or_404
from .models import product
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
# Create your views here.

def store(request, category_slug = None):
    categories = None
    products = None

    if category_slug != None:
        # It will bring the categories it found or it will display error
        categories = get_object_or_404(Category, slug = category_slug)
        # This will only pick those products which are in the distinct category
        products = product.objects.filter(category = categories, is_available = True)
        paginator = Paginator(products, 6)
        # Numbering the pages in url link
        page = request.GET.get('page')
        # Storing six products in paged_product
        paged_product = paginator.get_page(page)
        product_count = products.count()
    else:
        products = product.objects.all().filter(is_available = True).order_by('id')
        # Passing to paginator the number of products per page
        paginator = Paginator(products, 6)
        # Numbering the pages in url link
        page = request.GET.get('page')
        # Storing six products in paged_product
        paged_product = paginator.get_page(page)
        product_count = products.count()
    
    context = {
        # Changing products to paged_product
        'products': paged_product,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    try:
        single_product = product.objects.get(category__slug = category_slug, slug = product_slug)
        # If false then a product doesnt exist in cart. Otherwise it exists.
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e
    
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
    }

    return render(request, 'store/product_detail.html', context)