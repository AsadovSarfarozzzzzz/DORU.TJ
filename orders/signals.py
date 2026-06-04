from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order

@receiver(post_save, sender=Order)
def order_status_notification(sender, instance, created, **kwargs):
    if created:
        print(f"[СИГНАЛ] Новый заказ #{instance.pk} от {instance.user.username}")
    else:
        print(f"[СИГНАЛ] Заказ #{instance.pk} обновлён — статус: {instance.status}")