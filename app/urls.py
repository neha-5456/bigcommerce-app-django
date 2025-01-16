from django.urls import path

from app.views import  test , install , auth_callback 


urlpatterns = [
    # path('', install),
    path('test/', test),
   
    path('auth/callback/', install, name='auth_callback'),
   
    
]