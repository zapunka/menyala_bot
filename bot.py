from aiogram import Dispatcher, Bot, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, ContentType
from aiogram.dispatcher.filters.state import State, StatesGroup
import aiohttp
import asyncio
import json
import requests
import os
from dotenv import dotenv_values

from models import ExchangeResponse


config = {
    **dotenv_values(".env"),
    **os.environ,
}


storage = MemoryStorage()
bot = Bot(token=config.get('BOT_TOKEN'))
dispatcher = Dispatcher(bot=bot, storage=storage)


class BotSM(StatesGroup):
    convert_sum_state = State()


def setup(dp: Dispatcher):
    dp.register_message_handler(start_message, commands='start', state='*')
    dp.register_callback_query_handler(exchange_currency, lambda call_back: 'exchange' in call_back.data, state='*')
    dp.register_message_handler(convert_sum, lambda message: message.text
                                             and message.content_type == ContentType.TEXT
                                             and message.text.lower() != 'отменить',
                                state=BotSM.convert_sum_state)


async def start_message(message: Message):
    chat_id = message.chat.id
    client_name = message.chat.full_name
    message = f'Здравствуйте, {client_name}' if client_name else 'Здравствуйте!'
    message += '\n\nВыберите валюту, которую хотите поменять'

    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton(text='Рубли', callback_data='exchange_RUB'),
           InlineKeyboardButton(text='Гривны', callback_data='exchange_UAH'))
    kb.add(InlineKeyboardButton(text='Тенге', callback_data='exchange_KZT'),
           InlineKeyboardButton(text='USDT', callback_data='exchange_USDT'))

    await bot.send_message(chat_id=chat_id,
                           reply_markup=kb,
                           text=message)


async def exchange_currency(call_back: CallbackQuery, state: FSMContext):
    currency = call_back.data.split('_')[1]
    async with state.proxy() as data:
        data['exchange_currency'] = currency
        data['current_callback'] = call_back

    await bot.send_message(chat_id=call_back.message.chat.id,
                           text='Введите сумму, которую хотите обменять.')

    await BotSM.convert_sum_state.set()


async def convert_sum(message: Message, state: FSMContext):
    amount_str = message.text
    async with state.proxy() as data:
        currency = data['exchange_currency']
        call_back = data['current_callback']

    # пытаемся привести введенное пользователем значение к числу
    try:
        amount = float(amount_str)
    except (TypeError, ValueError):
        await bot.send_message(chat_id=message.chat.id,
                               text='Значение должно быть числом!')

        # call_back.data = f'exchange_{currency}'
        return await exchange_currency(call_back, state)

    # если валюта не USDT, то сначала смотрим курс к USDT, а потом USDT к бату
    # если валюта USDT - то сразу смотрим курс к бату
    if currency == 'USDT':
        pass
    else:
        usdt_to_curr = await get_currency_rate(currency, 'USDT')
        print(f'usdt_to_curr')
        # usdt_to_curr += config.get('UP_RATE')

    # usdt_to_thb = await get_currency_rate('THB', 'USDT')



async def get_currency_rate(base_curr: str, quote_curr: str):
    url = f'https://api.binance.com/api/v3/ticker/price?symbol={base_curr}{quote_curr}'

    r = requests.get(url)
    print(r.text)

    # async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
    #     async with session.get(url) as resp:
    #         body = await resp.json()
    #         print(f'resp = {body}')


async def get_thb_to_usdt():
    url = 'https://www.binance.com/ru/buy-sell-crypto/calculator/THB/USDT'
    # headers = {
    #     "accept": text/html, application/xhtml+xml, application/xml
    # q = 0.9, image / avif, image / webp, image / apng, * / *;q = 0.8, application / signed - exchange;
    #
    # accept - encoding: gzip, deflate, br
    # accept - language: ru - RU, ru;
    # q = 0.9, en - US;
    # q = 0.8, en;
    # q = 0.7
    # }

    # async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
    #     async with session.get(url) as resp:
    #         body = await resp.text()
    #         print(body)


if __name__ == '__main__':
    # setup(dispatcher)
    # executor.start_polling(dispatcher, skip_updates=True)
    asyncio.run(get_currency_rate('USD', 'RUB'))
    # asyncio.run(get_thb_to_usdt())
    # 'price': '73.76000000'

