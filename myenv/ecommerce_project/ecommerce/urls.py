from django.urls import path
from . import views

urlpatterns = [
    # 👇 Redirect root URL to login page first
    path('', views.login_view, name='login'),

    # 🛒 E-Commerce URLs
    path('home/', views.home, name='home'),   # ✅ Add home page separately
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('remove-from-cart/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),

    # 👤 Authentication
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),

    

]
