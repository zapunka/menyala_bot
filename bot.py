from aiogram import Dispatcher, Bot, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, ContentType
from aiogram.dispatcher.filters.state import State, StatesGroup
from enum import Enum
import os
from dotenv import dotenv_values

from exchange_api import exchange


config = {
    **dotenv_values(".env"),
    **os.environ,
}


storage = MemoryStorage()
bot = Bot(token=config.get('BOT_TOKEN'))
dispatcher = Dispatcher(bot=bot, storage=storage)

UP_RATE = 0.12


class GEOS(Enum):
    chaweng = 'Чавенг'
    lamai = 'Ламай'
    lipanoi = 'Липа Ной'
    naton = 'Натон'
    bangpo = 'Банг По'
    mainam = 'Маенам'
    boput = 'Бо Пут'
    chongmon = 'Чонг Мон'
    maret = 'Марет'
    talinggnam = 'Талинг Нгам'


class BotSM(StatesGroup):
    convert_sum_state = State()
    select_geo_state = State()


def setup(dp: Dispatcher):
    dp.register_message_handler(start_message, commands='start', state='*')
    dp.register_callback_query_handler(exchange_currency, lambda call_back: 'exchange' in call_back.data, state='*')
    dp.register_message_handler(convert_sum, lambda message: message.text
                                             and message.content_type == ContentType.TEXT
                                             and message.text.lower() != 'отменить',
                                state=BotSM.convert_sum_state)
    dp.register_callback_query_handler(select_geo,
                                       lambda call_back: 'select-geo' in call_back.data, state='*')
    dp.register_callback_query_handler(send_exchange_request,
                                       lambda call_back: 'send-request' in call_back.data, state='*')
    dp.register_callback_query_handler(go_home, lambda call_back: 'go-home' in call_back.data, state='*')


async def start_message(message: Message):
    chat_id = message.chat.id
    client_name = message.chat.full_name
    message = f'Приветствую, {client_name}' if client_name else 'Приветствую!'
    message += '\n\nМеня зовут Sawasdee caaaash бот. Здесь вы можете узнать актуальный курс обмена, а также, ' \
               'обменять свою валюту на баты. После формирования заявки менеджер свяжется с вами и доставит ' \
               'валюту менее, чем через час. Если у вас есть вопросы, вы можете связаться с менеджером ' \
               'напрямую: @newsoros'
    message += '\n\nВыберите валюту, которую хотите обменять:'

    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton(text='Рубли ₽', callback_data='exchange_RUB'),
           InlineKeyboardButton(text='Гривны ₴', callback_data='exchange_UAH'))
    kb.add(InlineKeyboardButton(text='Тенге ₸', callback_data='exchange_KZT'),
           InlineKeyboardButton(text='USDT', callback_data='exchange_USD'))

    await bot.send_message(chat_id=chat_id,
                           reply_markup=kb,
                           text=message)


async def exchange_currency(call_back: CallbackQuery, state: FSMContext):
    currency = call_back.data.split('_')[1]
    async with state.proxy() as data:
        data['exchange_currency'] = currency
        data['current_callback'] = call_back

    await bot.send_message(chat_id=call_back.message.chat.id,
                           text='Введите сумму, которую хотите обменять:')

    await BotSM.convert_sum_state.set()


async def convert_sum(message: Message, state: FSMContext):
    amount_str = message.text
    async with state.proxy() as data:
        currency = data['exchange_currency']
        call_back = data['current_callback']

    # пытаемся привести введенное пользователем значение к числу
    try:
        amount = float(amount_str)
        async with state.proxy() as data:
            data['exchange_amount'] = amount

    except (TypeError, ValueError):
        await bot.send_message(chat_id=message.chat.id,
                               text='Значение должно быть числом!')

        return await exchange_currency(call_back, state)

    if currency == 'USD':
        resp = await exchange("USD", "THB")
    else:
        resp = await exchange("THB", currency)

    if resp.status == 200:
        rate = float(resp.result) + UP_RATE

        if currency == 'USD':
            total_amount = round(amount * rate, 2)
        else:
            total_amount = round(amount / rate, 2)

        async with state.proxy() as data:
            data['exchange_rate'] = round(rate, 2)
            data['total_exchange_amount'] = total_amount

        msg = f'Курс обмена - {round(rate, 2)}\nВ итоге вы получите {total_amount} ฿\nОтправить заявку на обмен?'

        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(InlineKeyboardButton(text='В начало', callback_data='go-home'),
               InlineKeyboardButton(text='Отправить заявку', callback_data='select-geo'))

        await bot.send_message(chat_id=message.chat.id,
                               reply_markup=kb,
                               text=msg)

    else:
        msg = f'Ошибка при получении курса {currency}, статус = {resp.status}, ошибка = {resp.error}'
        await _send_error_msg(msg)
        msg += f'\nКлиент {message.chat.username} хотел обменять {currency} в количестве {amount}.' \
               f'\nНужно связаться с клиентом!'
        await _send_notify_msg(msg)

        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(InlineKeyboardButton(text='В начало', callback_data='go-home'))
        await bot.send_message(chat_id=message.chat.id,
                               reply_markup=kb,
                               text='Ваша заявка получена. В течение нескольких минут с вами '
                                    'свяжется менеджер! Спасибо!')


async def select_geo(call_back: CallbackQuery, state: FSMContext):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton(text='Чавенг', callback_data='send-request_chaweng'),
           InlineKeyboardButton(text='Ламай', callback_data='send-request_lamai'))
    kb.add(InlineKeyboardButton(text='Липа Нои', callback_data='send-request_lipanoi'),
           InlineKeyboardButton(text='Натон', callback_data='send-request_naton'))
    kb.add(InlineKeyboardButton(text='Банг По', callback_data='send-request_bangpo'),
           InlineKeyboardButton(text='Маенам', callback_data='send-request_mainam'))
    kb.add(InlineKeyboardButton(text='Бопут', callback_data='send-request_boput'),
           InlineKeyboardButton(text='Чонг Мон', callback_data='send-request_chongmon'))
    kb.add(InlineKeyboardButton(text='Марет', callback_data='send-request_maret'),
           InlineKeyboardButton(text='Талинг Нгам', callback_data='send-request_talinggnam'))
    kb.add(InlineKeyboardButton(text='В начало', callback_data='go-home'))
    await bot.send_message(chat_id=call_back.message.chat.id,
                           reply_markup=kb,
                           text='Выберите район, в котором вам будет удобно получить наличные.')


async def send_exchange_request(call_back: CallbackQuery, state: FSMContext):
    geo = call_back.data.split('_')[1]
    async with state.proxy() as data:
        currency = data['exchange_currency']
        amount = data['exchange_amount']
        rate = data['exchange_rate']
        total_amount = data['total_exchange_amount']

    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton(text='В начало', callback_data='go-home'))
    await bot.send_message(chat_id=call_back.message.chat.id,
                           reply_markup=kb,
                           text='Ваша заявка получена. В течение нескольких минут с вами свяжется менеджер. Спасибо!')

    msg = f'Клиент @{call_back.message.chat.username} запросил обмен валюты!' \
          f'\nОбмен {currency} в количестве {amount} по курсу {rate}: итого {total_amount} ฿' \
          f'\nРайон: {GEOS[geo].value}' \
          f'\nНеобходимо связаться с клиентом!'
    await _send_notify_msg(msg)




async def take_order(call_back: CallbackQuery, state: FSMContext):
    manager_username = call_back.message.chat.username


async def go_home(call_back: CallbackQuery):
    await start_message(call_back.message)


async def _send_error_msg(message: str):
    await bot.send_message(chat_id=config.get('DEVELOPER'),
                           text=message)


async def _send_notify_msg(message: str):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton(text='Взять в работу', callback_data='take-order'))

    for manager in config.get('MANAGERS').split(','):
        await bot.send_message(chat_id=manager,
                               # reply_markup=kb,
                               text=message)


if __name__ == '__main__':
    setup(dispatcher)
    executor.start_polling(dispatcher, skip_updates=True)


