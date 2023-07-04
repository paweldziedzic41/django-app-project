from django.shortcuts import render
from .forms import RegsitrationForm
# Create your views here.

def register(request):
    form = RegsitrationForm()
    context = {
        'form' : form,
    }
    return render(request, 'accounts/register.html')

def login(request):
    return render(request, 'accounts/login.html')
        
def logout(request):
    return 