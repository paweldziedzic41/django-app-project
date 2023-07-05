from django.shortcuts import render
from .forms import RegsitrationForm
from .models import Account
# Create your views here.

def register(request):
    if request.method == 'POST':
        # Sending the user info into the registration form class
        form = RegsitrationForm(request.POST)
        # If the from has all the required fields
        if form.is_valid():
            # cleaned_data lets to fetch value from the request
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            
            # Genrated username
            username = email.split("@")[0]

            # Creating a account
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.phone_number = phone_number
            user.save()
    else:
        # Only rendering the registration form
        form = RegsitrationForm()
    context = {
        'form' : form,
    }
    return render(request, 'accounts/register.html', context)

def login(request):
    return render(request, 'accounts/login.html')
        
def logout(request):
    return 