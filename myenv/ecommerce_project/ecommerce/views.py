from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import razorpay
from .models import Product, Order

# ------------------------------
# 🏠 HOME PAGE (Protected)
# ------------------------------
@login_required(login_url='login')
def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})


# ------------------------------
# 📦 PRODUCT DETAILS
# ------------------------------
@login_required(login_url='login')
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})


# ------------------------------
# 🛒 ADD TO CART
# ------------------------------
@login_required(login_url='login')
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = request.session.get('cart', {})

    if str(pk) in cart:
        cart[str(pk)]['quantity'] += 1
    else:
        cart[str(pk)] = {
            'name': product.name,
            'price': float(product.price),
            'quantity': 1,
            'image': product.image.url
        }

    request.session['cart'] = cart

    # ✅ AJAX Support for Add-to-Cart button
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        total_items = sum(item['quantity'] for item in cart.values())
        return JsonResponse({'success': True, 'cart_count': total_items})

    messages.success(request, f"{product.name} added to cart.")
    return redirect('view_cart')


# ------------------------------
# 🛍 VIEW CART
# ------------------------------
@login_required(login_url='login')
def view_cart(request):
    cart = request.session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    return render(request, 'cart.html', {'cart': cart, 'total': total})


# ------------------------------
# ❌ REMOVE ITEM FROM CART
# ------------------------------
@login_required(login_url='login')
def remove_from_cart(request, pk):
    cart = request.session.get('cart', {})
    if str(pk) in cart:
        del cart[str(pk)]
        request.session['cart'] = cart
        messages.info(request, "Item removed from cart.")
    return redirect('view_cart')


# ------------------------------
# 💳 CHECKOUT (Razorpay Integration)
# ------------------------------
@login_required(login_url='login')
def checkout(request):
    cart = request.session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())

    if total == 0:
        messages.error(request, "Your cart is empty.")
        return redirect('home')

    # Razorpay client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    amount_paise = int(total * 100)  # Convert rupees to paise

    # Create Razorpay Order
    payment = client.order.create({
        'amount': amount_paise,
        'currency': 'INR',
        'payment_capture': 1
    })

    # Save order in DB
    Order.objects.create(
        user=request.user,
        order_id=payment['id'],
        amount=total,
        status='Pending'
    )

    context = {
        'cart': cart,
        'total': total,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'razorpay_order_id': payment['id'],
        'razorpay_amount': amount_paise,
    }
    return render(request, 'checkout.html', context)


# ------------------------------
# ✅ PAYMENT SUCCESS HANDLER
# ------------------------------
@csrf_exempt
@login_required(login_url='login')
def payment_success(request):
    if request.method == "POST":
        payment_id = request.POST.get('razorpay_payment_id')
        order = Order.objects.filter(user=request.user).last()

        if order:
            order.razorpay_payment_id = payment_id
            order.status = "Paid"
            order.save()

        # Clear the cart
        request.session['cart'] = {}
        messages.success(request, "✅ Payment Successful! Thank you for shopping with us.")
        return render(request, 'payment_success.html', {'order': order})

    return redirect('home')

# ------------------------------
# 👤 USER REGISTRATION
# ------------------------------
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        user = User.objects.create_user(username=username, password=password)
        user.save()
        messages.success(request, "Account created successfully! You can now log in.")
        return redirect('login')

    return render(request, 'register.html')


# ------------------------------
# 🔑 USER LOGIN
# ------------------------------
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome, {username}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    return render(request, 'login.html')


# ------------------------------
# 🚪 USER LOGOUT
# ------------------------------
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')
