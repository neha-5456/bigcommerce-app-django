from django.urls import path

from app.views import index, test , install , auth_callback , custom_tab


urlpatterns = [
    path('', install),
    path('test/', test),
    # path('install/', install, name='install'),
    path('auth/callback/', auth_callback, name='auth_callback'),
    path('custom-tab/', custom_tab, name='custom_tab'),
    
]