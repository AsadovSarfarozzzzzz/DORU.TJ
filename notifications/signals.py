from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order
from .models import Notification


@receiver(post_save, sender=Order)
def create_order_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.user,
            title='Новый заказ создан',
            message=f'Заказ #{instance.pk} на сумму {instance.total} сомони ожидает подтверждения.',
            link=f'/orders/order/{instance.pk}/',
        )
    elif instance.status == 'confirmed':
        Notification.objects.create(
            user=instance.user,
            title='Заказ подтверждён',
            message=f'Заказ #{instance.pk} подтверждён. Готовим к доставке.',
            link=f'/orders/order/{instance.pk}/',
        )
    elif instance.status == 'delivering':
        Notification.objects.create(
            user=instance.user,
            title='Курьер в пути!',
            message=f'Заказ #{instance.pk} уже везут. Следите за курьером на карте.',
            link=f'/orders/order/{instance.pk}/',
        )
    elif instance.status == 'done':
        Notification.objects.create(
            user=instance.user,
            title='Заказ выполнен',
            message=f'Заказ #{instance.pk} доставлен. Приятного аппетита!',
            link=f'/orders/order/{instance.pk}/',
        )
    elif instance.status == 'cancelled':
        Notification.objects.create(
            user=instance.user,
            title='Заказ отменён',
            message=f'Заказ #{instance.pk} был отменён.',
            link=f'/orders/order/{instance.pk}/',
        )
