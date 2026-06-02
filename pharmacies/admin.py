from django.contrib import admin
from .models import Pharmacy, PharmacyProduct

admin.site.register(Pharmacy)
admin.site.register(PharmacyProduct)