import json
import urllib.request
from django.conf import settings


def send_order_notification(order, items):
    items_text = '\n'.join([
        f'• {item.product.name} x{item.quantity} — {item.price} сом'
        for item in items
    ])

    text = (
        f'🛒 Новый заказ #{order.pk}\n\n'
        f'👤 Клиент: {order.user.username}\n'
        f'📞 Телефон: {order.user.phone or "не указан"}\n'
        f'📍 Адрес: {order.address}\n\n'
        f'💊 Товары:\n{items_text}\n\n'
        f'💰 Итого: {order.total} сом'
    )

    keyboard = {
        'inline_keyboard': [[
            {
                'text': '✅ Принять',
                'callback_data': f'accept_{order.pk}'
            },
            {
                'text': '❌ Отклонить',
                'callback_data': f'reject_{order.pk}'
            }
        ]]
    }

    data = json.dumps({
        'chat_id': settings.TELEGRAM_GROUP_ID,
        'text': text,
        'reply_markup': keyboard,
        'parse_mode': 'HTML'
    }).encode('utf-8')

    req = urllib.request.Request(
        f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage',
        data=data,
        headers={'Content-Type': 'application/json'}
    )

    try:
        with urllib.request.urlopen(req) as res:
            print("✅ TG уведомление отправлено!")
    except Exception as e:
        print("❌ TG ошибка:", e)