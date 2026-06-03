from django.db import models
from products.models import Product
from django.conf import settings

# Create your models here.
class Pharmacy(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    latitude = models.FloatField()
    longitude = models.FloatField()
    working_hours = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_pharmacies'
    )

    def __str__(self):
        return self.name
    
class PharmacyProduct(models.Model):
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.pharmacy.name} — {self.product.name}'
    
from django.conf import settings

class PharmacyChat(models.Model):
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['pharmacy', 'user']

    def __str__(self):
        return f'{self.user.username} — {self.pharmacy.name}'


class PharmacyChatMessage(models.Model):
    SENDER_CHOICES = [
        ('user', 'Пользователь'),
        ('manager', 'Менеджер'),
    ]
    chat = models.ForeignKey(PharmacyChat, on_delete=models.CASCADE)
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    text = models.TextField(blank=True)
    image = models.ImageField(upload_to='pharmacy_chat/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender}: {self.text[:30]}'