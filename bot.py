import asyncio
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from django.conf import settings
from orders.models import Order

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Бот запущен")
    # Выведите в консоль, чтобы скопировать
@dp.message()
async def catch_all(message: types.Message):
    print(f"Бот получил сообщение из чата {message.chat.id}: {message.text}")

@dp.message()
async def echo(message: types.Message):
    # Для отладки - видит ли бот сообщения
    print(f"Получено сообщение от {message.chat.id}: {message.text}")

@dp.callback_query(lambda c: c.data.startswith('accept_'))
async def accept_order(callback: types.CallbackQuery):
    order_id = int(callback.data.split('_')[1])

    # меняем статус в базе
    order = await asyncio.to_thread(
        Order.objects.get, pk=order_id
    )
    order.status = 'delivering'
    await asyncio.to_thread(order.save)

    # обновляем кнопки
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[
        types.InlineKeyboardButton(
            text='✅ Доставил',
            callback_data=f'done_{order_id}'
        )
    ]])

    await callback.message.edit_text(
        callback.message.text + '\n\n🚚 Принят — доставляется',
        reply_markup=keyboard
    )
    await callback.answer('Заказ принят!')


@dp.callback_query(lambda c: c.data.startswith('reject_'))
async def reject_order(callback: types.CallbackQuery):
    order_id = int(callback.data.split('_')[1])

    order = await asyncio.to_thread(
        Order.objects.get, pk=order_id
    )
    order.status = 'cancelled'
    await asyncio.to_thread(order.save)

    await callback.message.edit_text(
        callback.message.text + '\n\n❌ Отклонён'
    )
    await callback.answer('Заказ отклонён!')


@dp.callback_query(lambda c: c.data.startswith('done_'))
async def done_order(callback: types.CallbackQuery):
    order_id = int(callback.data.split('_')[1])

    order = await asyncio.to_thread(
        Order.objects.get, pk=order_id
    )
    order.status = 'done'
    await asyncio.to_thread(order.save)

    await callback.message.edit_text(
        callback.message.text + '\n\n✅ Доставлен!'
    )
    await callback.answer('Заказ выполнен!')


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())