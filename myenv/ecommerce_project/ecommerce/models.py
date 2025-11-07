# from django.db import models
# from django.contrib.auth.models import User
# class Product(models.Model):
#     name = models.CharField(max_length=100)
#     description = models.TextField()
#     price = models.DecimalField(max_digits=8, decimal_places=2)
#     image = models.ImageField(upload_to='products/')


#     def __str__(self):
#         return self.name
    

# class Order(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     order_id = models.CharField(max_length=100)
#     razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     status = models.CharField(max_length=50, default='Pending')
#     created_at = models.DateTimeField(auto_now_add=True)
   
from django.db import models
from django.contrib.auth.models import User

# 🛍 Product Model
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    price = models.FloatField()
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return self.name


# 💳 Order Model
class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=100, unique=True)  # Razorpay order_id
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    amount = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username} - {self.status}"
