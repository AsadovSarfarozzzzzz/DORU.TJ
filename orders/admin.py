from django.contrib import admin
from .models import *

admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Courier)
admin.site.register(CourierLocation)
admin.site.register(Promocode)
admin.site.register(Reminder)