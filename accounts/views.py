from django.shortcuts import render, redirect
from .forms import RegsitrationForm
from .models import Account
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
            messages.success(request, 'Regsitration succesful.')
            return redirect('register')
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

        # If the user exist
        if user is not None:
            auth.login(request,user)
            return redirect('home')
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