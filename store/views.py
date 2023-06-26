from django.shortcuts import render, get_object_or_404
from .models import product
from category.models import Category
# Create your views here.

def store(request, category_slug = None):
    categories = None
    products = None

    if category_slug != None:
        # It will bring the categories it found or it will display error
        categories = get_object_or_404(Category, slug = category_slug)
        # This will only pick those products which are in the distinct category
        products = product.objects.filter(category = categories, is_available = True)
        product_count = products.count()
    else:
        products = product.objects.all().filter(is_available = True)
        product_count = products.count()
    
    context = {
        'products': products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)