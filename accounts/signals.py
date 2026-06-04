from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import User

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # можно добавить дефолтные значения
        if not instance.phone:
            instance.phone = ''
        if not instance.address:
            instance.address = ''
        instance.save()