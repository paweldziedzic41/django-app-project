from django.contrib import admin
from .models import product

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('product_name',)}
    list_display = ('product_name','price','stock','category','modified_date')

admin.site.register(product,ProductAdmin)