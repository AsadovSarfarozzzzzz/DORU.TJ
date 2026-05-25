from django.contrib import admin
from .admin import UserProfile, EmailConfirm

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(EmailConfirm)