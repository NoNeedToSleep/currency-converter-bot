import os
import asyncio
from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv
from aiogram.filters import Command
import aiohttp

load_dotenv()

TOKEN = os.getenv("TOKEN")
API_KEY = os.getenv("API_KEY")
API_URL = "https://api.exchangeratesapi.io/v1/latest"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    welcome_text = (
        "Привет! Я бот для конвертации валют.\n\n"
        "Вот как ты можешь использовать меня:\n\n"
        "/convert <amount> <from_currency> to <to_currency> - для конвертации валюты\n"
        "Пример: /convert 100 USD to EUR\n\n"
        "/rates - для получения текущих курсов валют\n\n"
        "/help - для получения этой инструкции"
    )
    await message.reply(welcome_text)

@dp.message(Command("help"))
async def send_help(message: types.Message):
    help_text = (
        "Доступные команды:\n\n"
        "/start - Приветствие и инструкция по использованию\n"
        "/convert <amount> <from_currency> to <to_currency> - для конвертации валюты\n"
        "Пример: /convert 100 USD to EUR\n\n"
        "/rates - для получения текущих курсов валют\n\n"
        "/help - для получения этой инструкции"
    )
    await message.reply(help_text)

@dp.message(Command("convert"))
async def convert_currency(message: types.Message):
    try:
        args = message.text.strip().split()

        if len(args) != 5 or args[3].lower() != 'to':
            await message.reply("Ошибка в формате команды. Используйте /convert <amount> <from_currency> to <to_currency>")
            return
        
        amount = float(args[1])
        from_currency = args[2].upper()
        to_currency = args[4].upper()

        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, params={"access_key": API_KEY, "base": "EUR"}) as response:
                if response.status != 200:
                    await message.reply("Не удалось получить данные от API.")
                    return
                data = await response.json()

        if from_currency in data['rates'] and to_currency in data['rates']:
            amount_in_eur = amount / data['rates'][from_currency]
            converted_amount = amount_in_eur * data['rates'][to_currency]
            await message.reply(f"{amount} {from_currency} = {converted_amount:.2f} {to_currency}")
        else:
            await message.reply("Одна из валют не найдена.")
    except ValueError:
        await message.reply("Ошибка в формате количества или валюты. Проверьте ввод.")
    except Exception as e:
        await message.reply(f"Произошла ошибка: {str(e)}")

@dp.message(Command("rates"))
async def get_rates(message: types.Message):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, params={"access_key": API_KEY}) as response:
                if response.status != 200:
                    await message.reply("Не удалось получить данные от API.")
                    return
                data = await response.json()

        rates = data['rates']
        rates_message = "\n".join([f"{currency}: {rate}" for currency, rate in rates.items()])
        await message.reply(f"Текущие курсы валют (базовая валюта {data['base']}):\n{rates_message}")
    except Exception as e:
        await message.reply(f"Не удалось получить курсы валют. Ошибка: {str(e)}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
