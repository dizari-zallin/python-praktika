"""
Лабораторная работа №17. Вариант 20.
Telegram-бот личного кабинета провайдера (aiogram 3).
Токен берётся из переменной BOT_TOKEN.
"""

import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from services import SERVICE_PRICE, TARIFFS, cabinet

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Текущий тариф"), KeyboardButton(text="История платежей")],
        [KeyboardButton(text="Подключить услугу"), KeyboardButton(text="Сменить тариф")],
    ],
    resize_keyboard=True,
)


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    # /start регистрирует абонента на базовом тарифе и показывает клавиатуру действий.
    @dp.message(CommandStart())
    async def start(message: Message):
        name = message.from_user.full_name if message.from_user else "Абонент"
        text = cabinet.register(message.from_user.id, name)
        await message.answer(text + "\nВыберите действие.", reply_markup=keyboard)

    @dp.message(F.text == "Текущий тариф")
    async def current(message: Message):
        await message.answer(cabinet.current_tariff(message.from_user.id))

    @dp.message(F.text == "История платежей")
    async def history(message: Message):
        await message.answer(cabinet.history(message.from_user.id))

    @dp.message(Command("service"))
    async def service_cmd(message: Message):
        parts = (message.text or "").split(maxsplit=1)
        if len(parts) < 2:
            await message.answer("Формат: /service антивирус\nДоступны: " + ", ".join(SERVICE_PRICE))
            return
        await message.answer(cabinet.connect_service(message.from_user.id, parts[1].strip()))

    @dp.message(F.text == "Подключить услугу")
    async def service_hint(message: Message):
        await message.answer("Напишите /service и название. Например: /service ТВ")

    @dp.message(Command("tariff"))
    async def tariff_cmd(message: Message):
        parts = (message.text or "").split(maxsplit=1)
        if len(parts) < 2:
            await message.answer("Формат: /tariff Домашний 300\nДоступны: " + ", ".join(TARIFFS))
            return
        await message.answer(cabinet.change_tariff(message.from_user.id, parts[1].strip()))

    @dp.message(F.text == "Сменить тариф")
    async def tariff_hint(message: Message):
        await message.answer("Напишите /tariff и название. Например: /tariff Домашний 300")

    return dp


async def main():
    token = os.environ.get("BOT_TOKEN", "")
    if not token:
        print("Задайте BOT_TOKEN. Локальная демонстрация без Telegram: python demo.py")
        return
    bot = Bot(token)
    await build_dispatcher().start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
