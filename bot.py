import asyncio
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from django.conf import settings

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# Принять заказ
@dp.callback_query(F.data.startswith('accept_'))
async def accept_order(callback: types.CallbackQuery):
    from orders.models import Order, DeliveryChat
    order_id = int(callback.data.split('_')[1])

    order = await asyncio.to_thread(Order.objects.get, pk=order_id)
    order.status = 'delivering'
    await asyncio.to_thread(order.save)

    # создаём чат
    await asyncio.to_thread(
        DeliveryChat.objects.get_or_create, order=order
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text='📍 Обновить локацию', callback_data=f'location_{order_id}'),
        InlineKeyboardButton(text='✅ Доставил', callback_data=f'done_{order_id}'),
    ]])

    await callback.message.edit_text(
        callback.message.text + '\n\n🚚 Принято! Заказ доставляется.',
        reply_markup=keyboard
    )
    await callback.answer('Заказ принят!')


# Отклонить заказ
@dp.callback_query(F.data.startswith('reject_'))
async def reject_order(callback: types.CallbackQuery):
    from orders.models import Order
    order_id = int(callback.data.split('_')[1])

    order = await asyncio.to_thread(Order.objects.get, pk=order_id)
    order.status = 'cancelled'
    await asyncio.to_thread(order.save)

    await callback.message.edit_text(
        callback.message.text + '\n\n❌ Отклонён.'
    )
    await callback.answer('Заказ отклонён!')


# Доставил
@dp.callback_query(F.data.startswith('done_'))
async def done_order(callback: types.CallbackQuery):
    from orders.models import Order
    order_id = int(callback.data.split('_')[1])

    order = await asyncio.to_thread(Order.objects.get, pk=order_id)
    order.status = 'done'
    await asyncio.to_thread(order.save)

    await callback.message.edit_text(
        callback.message.text + '\n\n✅ Выполнен!'
    )
    await callback.answer('Отлично!')


# Курьер отправляет сообщение клиенту
@dp.message(F.text.startswith('/msg'))
async def courier_message(message: types.Message):
    # формат: /msg 5 Буду через 10 минут
    parts = message.text.split(' ', 2)
    if len(parts) < 3:
        await message.answer('Формат: /msg <номер_заказа> <сообщение>')
        return

    order_id = int(parts[1])
    text = parts[2]

    from orders.models import Order, DeliveryChat, DeliveryChatMessage
    order = await asyncio.to_thread(Order.objects.get, pk=order_id)
    chat, _ = await asyncio.to_thread(
        DeliveryChat.objects.get_or_create, order=order
    )
    await asyncio.to_thread(
        DeliveryChatMessage.objects.create,
        chat=chat,
        sender='courier',
        text=text
    )
    await message.answer(f'✅ Сообщение отправлено клиенту заказа #{order_id}')


# Курьер обновляет локацию через геолокацию Telegram
@dp.message(F.location)
async def courier_location(message: types.Message):
    lat = message.location.latitude
    lng = message.location.longitude

    await message.answer(
        f'📍 Локация получена!\n'
        f'Отправь номер заказа для обновления:\n'
        f'/setloc <номер_заказа>'
    )
    # сохраняем в FSM
    await message.answer(f'lat={lat}, lng={lng}')


@dp.message(F.text.startswith('/setloc'))
async def set_location(message: types.Message):
    parts = message.text.split(' ')
    if len(parts) < 2:
        await message.answer('Формат: /setloc <номер_заказа>')
        return

    order_id = int(parts[1])

    # берём последнюю геолокацию из текста (упрощённо)
    await message.answer(
        'Отправь геолокацию через скрепку 📎 → Местоположение'
    )


# Обновить локацию напрямую
@dp.message(F.text.startswith('/loc'))
async def update_location(message: types.Message):
    # формат: /loc 5 38.5598 68.7870
    parts = message.text.split(' ')
    if len(parts) < 4:
        await message.answer('Формат: /loc <заказ> <lat> <lng>')
        return

    order_id = int(parts[1])
    lat = float(parts[2])
    lng = float(parts[3])

    from orders.models import Order, CourierLocation
    order = await asyncio.to_thread(Order.objects.get, pk=order_id)
    await asyncio.to_thread(
        CourierLocation.objects.update_or_create,
        order=order,
        defaults={'latitude': lat, 'longitude': lng}
    )
    await message.answer(f'✅ Локация обновлена для заказа #{order_id}')


@dp.message(Command('start'))
async def start(message: types.Message):
    await message.answer(
        '🛵 Привет курьер!\n\n'
        'Команды:\n'
        '/msg <заказ> <текст> — написать клиенту\n'
        '/loc <заказ> <lat> <lng> — обновить локацию\n'
        'Или просто отправь геолокацию 📍'
    )


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())