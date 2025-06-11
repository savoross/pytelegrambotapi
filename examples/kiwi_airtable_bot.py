import os
import time
import random
import requests
import telebot
from telebot import types

# Replace with your token and Airtable credentials or set environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'TOKEN')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID', 'BASE_ID')
AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY', 'API_KEY')
AIRTABLE_CLIENTS_TABLE = 'Clients'
AIRTABLE_PARCELS_TABLE = 'Посылки'

bot = telebot.TeleBot(BOT_TOKEN)


def setup_bot() -> None:
    """Configure bot description and command menu."""
    bot.set_my_description('\u0411\u043E\u0442 \u0434\u043B\u044F \u043E\u0442\u0441\u043B\u0435\u0436\u0438\u0432\u0430\u043D\u0438\u044F \u043F\u043E\u0441\u044B\u043B\u043E\u043A')
    bot.set_my_short_description('\u041F\u043E\u0441\u044B\u043B\u043A\u0438 \u0438\u0437 \u041A\u0438\u0442\u0430\u044F')
    bot.set_my_commands([
        types.BotCommand('start', '\u041C\u0435\u043D\u044E'),
        types.BotCommand('\u0438\u0441\u0442\u043E\u0440\u0438\u044F', '\u041C\u043E\u0438 \u043F\u043E\u0441\u044B\u043B\u043A\u0438'),
        types.BotCommand('admin', '\u0410\u0434\u043C\u0438\u043D\u0438\u0441\u0442\u0440\u0430\u0442\u0438\u0432\u043D\u044B\u0435 \u043A\u043E\u043C\u0430\u043D\u0434\u044B'),
    ])


setup_bot()

# Blocked user ids
BLOCKED = set()
# Last message time per user for anti spam
_last_time = {}


def _check_spam(message: types.Message) -> bool:
    """Returns True if message should be ignored."""
    uid = message.from_user.id
    if uid in BLOCKED:
        bot.send_message(message.chat.id, 'заблокирован')
        return True
    now = time.time()
    if now - _last_time.get(uid, 0) < 10:
        return True
    _last_time[uid] = now
    return False


@bot.message_handler(commands=['start'])
def start_cmd(message: types.Message):
    if _check_spam(message):
        return
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('\U0001F4E6 \u0420\u0435\u0433\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u044f', callback_data='register'))
    markup.add(types.InlineKeyboardButton('\U0001F4C4 \u041F\u0440\u043E\u0444\u0438\u043B\u044C', callback_data='profile'))
    markup.add(types.InlineKeyboardButton('\U0001F69A \u041E\u0442\u0441\u043B\u0435\u0434\u0438\u0442\u044C', callback_data='track'))
    markup.add(types.InlineKeyboardButton('\uD83D\uDD28 \u041F\u043E\u0434\u0434\u0435\u0440\u0436\u043A\u0430', callback_data='support'))
    bot.send_message(message.chat.id, '\u0414\u043E\u0431\u0440\u043E \u043F\u043E\u0436\u0430\u043B\u043E\u0432\u0430\u0442\u044C!', reply_markup=markup)


@bot.callback_query_handler(func=lambda c: c.data == 'register')
def ask_contact(call: types.CallbackQuery):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton('\uD83D\uDCDE \u041E\u0442\u043F\u0440\u0430\u0432\u0438\u0442\u044C \u043A\u043E\u043D\u0442\u0430\u043A\u0442', request_contact=True))
    bot.send_message(call.message.chat.id, '\u041F\u043E\u0434\u0435\u043B\u0438\u0442\u0435\u0441\u044C \u043A\u043E\u043D\u0442\u0430\u043A\u0442\u043E\u043C', reply_markup=markup)


@bot.callback_query_handler(func=lambda c: c.data == 'profile')
def profile_cb(call: types.CallbackQuery):
    bot.answer_callback_query(call.id)
    uid = call.from_user.id
    params = {'filterByFormula': f"{{Telegram ID}}='{uid}'"}
    url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_CLIENTS_TABLE}'
    headers = {'Authorization': f'Bearer {AIRTABLE_API_KEY}'}
    text = '\u041F\u0440\u043E\u0444\u0438\u043B\u044C \u043D\u0435 \u043D\u0430\u0439\u0434\u0435\u043D'
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        records = resp.json().get('records', [])
        if records:
            fields = records[0]['fields']
            text = (f"\u0418\u043C\u044F: {fields.get('Name', '')}\n"
                    f"\u0422\u0435\u043B\u0435\u0444\u043E\u043D: {fields.get('Phone', '')}\n"
                    f"clientCode: {fields.get('clientCode', '')}")
    except requests.RequestException:
        text = '\u041E\u0448\u0438\u0431\u043A\u0430 \u0437\u0430\u043F\u0440\u043E\u0441\u0430'
    bot.send_message(call.message.chat.id, text)


@bot.callback_query_handler(func=lambda c: c.data == 'track')
def track_cb(call: types.CallbackQuery):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, '\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043A\u043E\u043C\u0430\u043D\u0434\u0443 \"\u0442\u0440\u0435\u043A <\u043D\u043E\u043C\u0435\u0440>\"')


@bot.callback_query_handler(func=lambda c: c.data == 'support')
def support_cb(call: types.CallbackQuery):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, '\u041F\u0438\u0448\u0438\u0442\u0435 \u043D\u0430 @support')


@bot.message_handler(content_types=['contact'])
def handle_contact(message: types.Message):
    if _check_spam(message):
        return
    contact = message.contact
    client_code = f"KIWI-{random.randint(100, 999)}"
    data = {
        'fields': {
            'Telegram ID': str(message.from_user.id),
            'Name': message.from_user.first_name or '',
            'Phone': contact.phone_number,
            'clientCode': client_code,
        }
    }
    url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_CLIENTS_TABLE}'
    headers = {
        'Authorization': f'Bearer {AIRTABLE_API_KEY}',
        'Content-Type': 'application/json'
    }
    try:
        requests.post(url, json=data, headers=headers, timeout=10)
    except requests.RequestException:
        pass
    bot.send_message(message.chat.id, f'\u0412\u0430\u0448 \u043A\u043E\u0434: {client_code}', reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=['profile'])
def profile_cmd(message: types.Message):
    if _check_spam(message):
        return
    uid = message.from_user.id
    params = {'filterByFormula': f"{{Telegram ID}}='{uid}'"}
    url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_CLIENTS_TABLE}'
    headers = {'Authorization': f'Bearer {AIRTABLE_API_KEY}'}
    text = '\u041F\u0440\u043E\u0444\u0438\u043B\u044C \u043D\u0435 \u043D\u0430\u0439\u0434\u0435\u043D'
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        records = resp.json().get('records', [])
        if records:
            fields = records[0]['fields']
            text = (f"\u0418\u043C\u044F: {fields.get('Name', '')}\n"
                    f"\u0422\u0435\u043B\u0435\u0444\u043E\u043D: {fields.get('Phone', '')}\n"
                    f"clientCode: {fields.get('clientCode', '')}")
    except requests.RequestException:
        text = '\u041E\u0448\u0438\u0431\u043A\u0430 \u0437\u0430\u043F\u0440\u043E\u0441\u0430'
    bot.send_message(message.chat.id, text)


@bot.message_handler(regexp=r'^\s*\u0442\u0440\u0435\u043A\s+(\S+)')
def track_cmd(message: types.Message):
    if _check_spam(message):
        return
    track_number = message.text.split(maxsplit=1)[1]
    formula = f"{{\u0422\u0440\u0435\u043A-\u043D\u043E\u043C\u0435\u0440 (\u041A\u0438\u0442\u0430\u0439)}}='{track_number}'"
    url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_PARCELS_TABLE}'
    params = {'filterByFormula': formula}
    headers = {'Authorization': f'Bearer {AIRTABLE_API_KEY}'}
    status = 'not found'
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        records = resp.json().get('records', [])
        if records:
            fields = records[0]['fields']
            status = fields.get('Status', 'unknown')
    except requests.RequestException:
        status = 'error'
    bot.send_message(message.chat.id, status)


@bot.message_handler(commands=['\u0438\u0441\u0442\u043E\u0440\u0438\u044F'])
def history_cmd(message: types.Message):
    if _check_spam(message):
        return
    uid = message.from_user.id
    formula = f"{{Telegram ID}}='{uid}'"
    url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_PARCELS_TABLE}'
    params = {'filterByFormula': formula}
    headers = {'Authorization': f'Bearer {AIRTABLE_API_KEY}'}
    text = []
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        for rec in resp.json().get('records', []):
            fields = rec['fields']
            tnum = fields.get('\u0422\u0440\u0435\u043A-\u043D\u043E\u043C\u0435\u0440 (\u041A\u0438\u0442\u0430\u0439)', '')
            status = fields.get('Status', '')
            text.append(f"{tnum}: {status}")
    except requests.RequestException:
        pass
    if not text:
        text = ['\u041D\u0435\u0442 \u043F\u043E\u0441\u044B\u043B\u043E\u043A']
    bot.send_message(message.chat.id, '\n'.join(text))


@bot.message_handler(commands=['admin'])
def admin_cmd(message: types.Message):
    if _check_spam(message):
        return
    if message.from_user.id != 123456789:
        return
    bot.send_message(message.chat.id, 'ban, user, trackstat, lastregs')


bot.infinity_polling(skip_pending=True)
