from django.urls import path

from app.views import index, test


urlpatterns = [
    path('', index),
    path('/test/', test),
    
]