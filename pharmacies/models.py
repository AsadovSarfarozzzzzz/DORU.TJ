from django.db import models
from products.models import Product

# Create your models here.
class Pharmacy(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    latitude = models.FloatField()
    longitude = models.FloatField()
    working_hours = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name