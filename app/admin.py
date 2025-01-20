from django.contrib import admin
from .models import Store , StoreUser ,User

class StoreAdmin(admin.ModelAdmin):
    list_display = ('store_hash', 'access_token', 'scope')  
    # search_fields = ('store_hash') 

admin.site.register(Store, StoreAdmin)
class StoreUserAdmin(admin.ModelAdmin):
    list_display = ('store', 'user', 'admin')  
    # search_fields = ('user') 
    
    
admin.site.register(StoreUser, StoreUserAdmin)


class UserAdmin(admin.ModelAdmin):
    list_display = ('bc_id', 'email')  
    # search_fields = ('email') 
    
    
admin.site.register(User, UserAdmin)