from .models import Category
from django.shortcuts import render

def menu_links(request):
    # Storing the category into the links list
    links = Category.objects.all
    # Return a dictioniary variable type
    return dict(links = links)