from django.contrib import admin
from .models import Account
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class AccountAdmin(UserAdmin):
    # List of displayed fields in the admin panel
    list_display = ('email', 'first_name', 'last_name', 'username', 
                    'last_login', 'date_joined' ,'is_active')
    
    # List of parameters in the admin panel that you can interact with
    list_display_links = ('email', 'first_name', 'last_name')
    
    # Fields only for read 
    readonly_fields = ('last_login', 'date_joined')
    
    # Default ordering of the data in the admin panel
    
    ordering = ('-date_joined',)
    
    # Makes password read only
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(Account, AccountAdmin)