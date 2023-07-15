from django.shortcuts import render, redirect
from .forms import RegsitrationForm
from .models import Account
from carts.models import Cart, CartItem
from carts.views import _cart_id, change_cart_items_when_logged
from django.contrib import messages, auth
from django.http import HttpResponse
# Django modules for token validation
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.contrib.auth.hashers import check_password
import requests
# Create your views here.

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        verify = Account._default_manager.filter(email = email).exists()
        if verify == True:
            user = Account._default_manager.get(email=email)
            # Forming a mail message
            current_site = get_current_site(request)
            mail_subject = "Change password"
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            messages.success(request,"Your link to password reset was sent on mail account")
            return redirect('login')
        else:
            messages.error(request, 'Email does not exist in the database')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')



def validateEmail(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk = uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        return redirect('/accounts/forgotPassword/?command=changePassword&email='+user.email)
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('forgetPassword')

def changePassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confrim_password = request.POST['confirm_password']
        if password == confrim_password:
            email = request.POST['email']
            user = Account._default_manager.get(email=email)
            user.set_password(password)
            user.save()
            messages.success(request, "Password has been changed succesfully.")
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match. Try again')
            return redirect('/accounts/forgotPassword/?command=changePassword&email='+user.email)

@login_required(login_url = 'login')
def dashboard(request):
    print(request)
    return render(request, 'accounts/dashboard.html')

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
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email,  username=username,  password=password)
            user.phone_number = phone_number
            user.save()
            # User activation
            # current_size - the url to the shop site
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            # The message will be rendered as a HTML file in the given path
            
            message = render_to_string('accounts/account_verification_email.html' , {
                # Some of the user info will be send to the HTML file 
                'user': user,
                'domain': current_site,
                # Encoding the primary key
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                # Create a token from the user
                'token': default_token_generator.make_token(user),
            })
            # The email to which the message is being sent
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            # Sending the info into the registration site
            return redirect('/accounts/login/?command=verification&email='+email)
    else:
        # Only rendering the registration form
        form = RegsitrationForm()
    context = {
        'form' : form,
    }
    return render(request, 'accounts/register.html', context)

def login(request):
    if request.method == 'POST':
        # Getting email and password from the input fields
        email = request.POST['email']
        password = request.POST['password']
        # Authentication if the email and password, exist in database and are correct
        user = auth.authenticate(email = email, password = password)

        try:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            session_cart_items = CartItem.objects.filter(cart = cart)
        except:
            pass
        # If the user exist         
        if user is not None:
            try:
                if CartItem.objects.filter(cart = cart).exists():
                    change_cart_items_when_logged(session_cart_items, user, cart)
                    cart.delete()
            except:
                pass    
            
            auth.login(request,user)
            messages.success(request, "You are logged on")
            
            # Gets the url from the previous site
            url = request.META.get('HTTP_REFERER')
            if 'next' in url:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                return redirect(params['next'])
            else:
                return redirect('dashboard')
               
        # If the user doesn't exist
        else:
            messages.error(request, "Invalid login")
            return redirect('login')
    return render(request, 'accounts/login.html')

# The @login_required dekorator is to restrict access to the logout function
# so only the authenticated user can access them
@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, "You are logged out")
    return redirect('login')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk = uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request,'Congratulations your account is activated')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')

