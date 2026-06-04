from django.db import models
from products.models import Product
from django.conf import settings
import secrets
from django.utils import timezone


class Promocode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_uses = models.PositiveIntegerField(default=100)
    used_count = models.PositiveIntegerField(default=0)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        if not self.is_active:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        if self.used_count >= self.max_uses:
            return False
        return True

    def apply(self, total):
        discount = max(self.discount_amount, total * self.discount_percent / 100)
        return max(total - discount, 0)

    def __str__(self):
        return self.code


class Reminder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reminders')
    text = models.CharField(max_length=500)
    remind_at = models.DateTimeField()
    is_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['remind_at']

    def __str__(self):
        return f'{self.user.username} — {self.text[:30]}'


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} -- {self.created_at}'
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('confirmed', 'Подтверждён'),
        ('delivering', 'Доставляется'),
        ('done', 'Выполнен'),
        ('cancelled', 'Отменён'),
    ]
    PAYMENT_CHOICES = [
        ('cash', 'Наличными'),
        ('card', 'Картой'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    prescription = models.ImageField(upload_to='prescriptions/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    courier_token = models.CharField(max_length=64, blank=True)

    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_CHOICES,
        default='cash'
    )

    def save(self, *args, **kwargs):
        if not self.courier_token:
            self.courier_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

class DeliveryChat(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Чат заказа #{self.order.pk}'
    
class DeliveryChatMessage(models.Model):
    SENDER_CHOICES = [
        ('client', 'Клиент'),
        ('courier', 'Курьер'),
    ]
    chat = models.ForeignKey(DeliveryChat, on_delete=models.CASCADE)
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    text = models.TextField(blank=True)
    image = models.ImageField(upload_to='chat_images/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender}: {self.text[:30]}'
    

class CourierLocation(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Локация заказа #{self.order.pk}'
    
class Courier(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    current_order = models.ForeignKey(
        'Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_courier'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Курьер: {self.user.username}'