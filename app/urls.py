from django.urls import path
from . import views
# from app.views import index, test


urlpatterns = [
    path('', views.index),
    path('/test/', views.test),
   
]