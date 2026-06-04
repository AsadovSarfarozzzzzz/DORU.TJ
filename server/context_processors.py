from django.urls import reverse
from django.utils.translation import gettext_lazy as _


def mobile_nav_items(request):
    if request.user.is_authenticated and not request.user.is_courier and not request.user.is_manager:
        items = [
            {'url': reverse('catalog'), 'icon': 'ti ti-pill', 'label': _('Каталог')},
            {'url': reverse('pharmacy_list'), 'icon': 'ti ti-building-hospital', 'label': _('Аптеки')},
            {'url': reverse('consultant'), 'icon': 'ti ti-robot', 'label': _('AI Консультант')},
            {'url': reverse('my_orders'), 'icon': 'ti ti-package', 'label': _('Заказы')},
            {'url': reverse('favorites'), 'icon': 'ti ti-star', 'label': _('Избранное')},
            {'url': reverse('symptom_search'), 'icon': 'ti ti-stethoscope', 'label': _('Симптомы')},
            {'url': reverse('reminders'), 'icon': 'ti ti-bell-plus', 'label': _('Напоминания')},
        ]
        return {'mobile_nav_items': items}
    return {}
