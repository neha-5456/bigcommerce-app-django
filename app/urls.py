from django.urls import path
from . import views
# from app.views import index, test


urlpatterns = [
    path('', views.index),
    path('/test/', views.test),
    # path('auth/', views.bigcommerce_auth, name='bigcommerce_auth'),
    # path('auth/callback/', views.auth_callback, name='auth_callback'),
    # path('products/', views.products, name='products'),
]