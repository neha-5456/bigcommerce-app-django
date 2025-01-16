from django.urls import path

from app.views import  test , install , auth_callback 


urlpatterns = [
    path('', install),
    path('test/', test),
    # path('install/', install, name='install'),
    path('auth/callback/', auth_callback, name='auth_callback'),
   
    
]