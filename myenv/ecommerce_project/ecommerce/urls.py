from django.urls import path
from . import views

urlpatterns = [
    # 👤 Authentication
    path('', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # 🏠 Home & Products
    path('home/', views.home, name='home'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    # 🛒 Cart Management
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('remove-from-cart/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),

    # 💳 Checkout & Payment
    path('checkout/', views.checkout, name='checkout'),
    path('payment-success/', views.payment_success, name='payment_success'),

]
