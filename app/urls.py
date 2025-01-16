from django.urls import path

from app.views import  index , install , load


urlpatterns = [
    # path('', install),
    path('', index),
    path('auth/callback/', install, name='auth_callback'),
    path('load/', load, name='load_app'),
   
    
]