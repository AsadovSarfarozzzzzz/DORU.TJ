from django.contrib import admin
from .models import Product, Category, Manufacturer, Review, Favorite

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Manufacturer)
admin.site.register(Review)
admin.site.register(Favorite)