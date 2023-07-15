from django.shortcuts import render, redirect
from carts.models import CartItem
from django.http import HttpResponse
from .forms import OrderForm
from .models import Order
import datetime
# Create your views here.

def payments(request):
     return render(request, 'orders/payments.html')

def taxes(cart_items, tax = 0, grand_total = 0):
        total = 0
        for cart_item in cart_items:
            total += (cart_item.product.price*cart_item.quantity)
        tax = (0.08 * total)
        grand_total = total - tax
        return tax, grand_total

def place_order(request):
    if request.method == 'POST':
        tax = 0
        grand_total = 0
        cart_items = CartItem.objects.all().filter(user = request.user)
        tax, grand_total = taxes(cart_items, tax, grand_total)
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = request.user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            user_order = Order.objects.get(user = request.user, order_number = order_number)

            context = {
                 'user_order': user_order,
                 'cart_items': cart_items,
            }

            return render(request, 'orders/payments.html', context)
        