from django.urls import path

from app.views import  index , install 


urlpatterns = [
    # path('', install),
    path('', index),
   
    path('auth/callback/', install, name='auth_callback'),
   
    
]