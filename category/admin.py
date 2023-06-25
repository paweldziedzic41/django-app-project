from django.contrib import admin
from . models import Category

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    # Varaible sets field slug to copy from filed categoty_name
    prepopulated_fields = {'slug':('category_name',)}
    # Displaying category_name and slug on front page of categories
    list_display = ('category_name', 'slug')


admin.site.register(Category, CategoryAdmin)
