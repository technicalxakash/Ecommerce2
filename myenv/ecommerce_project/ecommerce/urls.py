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


    path('my-orders/', views.my_orders, name='my_orders'),

    path('my-orders/', views.my_orders, name='my_orders'),
   path('download-invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),


    # 👤 User Profile (NEW)
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    # 🏠 Address Management (NEW)
    path('addresses/', views.address_list, name='address_list'),
    path('address/add/', views.add_address, name='add_address'),
    path('address/edit/<int:pk>/', views.edit_address, name='edit_address'),
    path('address/delete/<int:pk>/', views.delete_address, name='delete_address'),


]
