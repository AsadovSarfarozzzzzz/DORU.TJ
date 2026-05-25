from django.contrib import admin
from .admin import User, EmailConfirm

# Register your models here.
admin.site.register(User)
admin.site.register(EmailConfirm)