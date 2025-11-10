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
from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa
#=======================



from django.http import HttpResponse, JsonResponse



import io,os   # ✅ Add this line


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
#===============================================
@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_orders.html', {'orders': orders})


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




# ------------------------------
# 📋 MY ORDERS PAGE
# ------------------------------
@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_orders.html', {'orders': orders})


# ------------------------------
# 🧾 DOWNLOAD INVOICE AS PDF
# ------------------------------
import io
import base64
from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.conf import settings
import os
from .models import Order


@login_required(login_url='login')
def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # ✅ Convert logo to Base64 string
    logo_path = os.path.join(settings.BASE_DIR, 'ecommerce', 'static', 'images', 'logo.jpg')
    with open(logo_path, "rb") as image_file:
        logo_data = base64.b64encode(image_file.read()).decode('utf-8')
    logo_base64 = f"data:image/jpeg;base64,{logo_data}"

    # Render the HTML with Base64 image
    html = render_to_string('invoice_template.html', {
        'order': order,
        'logo_path': logo_base64  # base64 logo
    })

    # Generate PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{order.order_id}.pdf"'
    pisa_status = pisa.CreatePDF(io.BytesIO(html.encode("UTF-8")), dest=response)

    if pisa_status.err:
        return HttpResponse("⚠️ Error generating invoice. Please try again.")
    return response


import json
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Order, Product

@login_required(login_url='login')
def admin_dashboard(request):
    # ✅ Only admin/superuser can access
    if not request.user.is_superuser:
        messages.error(request, "Access Denied: Admins only.")
        return redirect('home')

    # Summary data
    total_users = User.objects.count()
    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(status="Paid").aggregate(Sum('amount'))['amount__sum'] or 0

    # Monthly revenue data
    monthly_data = (
        Order.objects.filter(status="Paid")
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    months = [entry['month'].strftime("%b %Y") for entry in monthly_data]
    revenues = [float(entry['total']) for entry in monthly_data]

    # Top 5 Selling Products (placeholder if no product-order link)
    top_products = Product.objects.all()[:5]
    top_products_names = [p.name for p in top_products]
    top_products_sales = [float(p.price) for p in top_products]

    # Recent orders
    recent_orders = Order.objects.order_by('-created_at')[:5]

    # ✅ Convert to JSON for Chart.js
    context = {
        'total_users': total_users,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'months': json.dumps(months),
        'revenues': json.dumps(revenues),
        'top_products_names': json.dumps(top_products_names),
        'top_products_sales': json.dumps(top_products_sales),
        'recent_orders': recent_orders,
    }

    return render(request, 'admin_dashboard.html', context)



from .models import UserProfile, Address
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

# 🧑‍💼 Profile View
@login_required(login_url='login')
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'profile.html', {'profile': profile, 'addresses': addresses})


# ✏️ Edit Profile
@login_required(login_url='login')
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        profile.phone = request.POST.get('phone')
        profile.address = request.POST.get('address')

        if 'profile_image' in request.FILES:
            profile.profile_image = request.FILES['profile_image']

        profile.save()
        messages.success(request, "✅ Profile updated successfully!")
        return redirect('profile')

    return render(request, 'edit_profile.html', {'profile': profile})


# 🏠 Address List
@login_required(login_url='login')
def address_list(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'address_list.html', {'addresses': addresses})


# ➕ Add Address
@login_required(login_url='login')
def add_address(request):
    if request.method == "POST":
        Address.objects.create(
            user=request.user,
            full_name=request.POST['full_name'],
            phone=request.POST['phone'],
            pincode=request.POST['pincode'],
            street=request.POST['street'],
            city=request.POST['city'],
            state=request.POST['state'],
            landmark=request.POST.get('landmark', ''),
            is_default='is_default' in request.POST
        )
        messages.success(request, "✅ Address added successfully!")
        return redirect('address_list')
    return render(request, 'add_address.html')


# 📝 Edit Address
@login_required(login_url='login')
def edit_address(request, pk):
    address = Address.objects.get(pk=pk, user=request.user)
    if request.method == "POST":
        address.full_name = request.POST['full_name']
        address.phone = request.POST['phone']
        address.pincode = request.POST['pincode']
        address.street = request.POST['street']
        address.city = request.POST['city']
        address.state = request.POST['state']
        address.landmark = request.POST.get('landmark', '')
        address.is_default = 'is_default' in request.POST
        address.save()
        messages.success(request, "✅ Address updated successfully!")
        return redirect('address_list')
    return render(request, 'edit_address.html', {'address': address})


# ❌ Delete Address
@login_required(login_url='login')
def delete_address(request, pk):
    Address.objects.get(pk=pk, user=request.user).delete()
    messages.warning(request, "🗑️ Address deleted.")
    return redirect('address_list')
