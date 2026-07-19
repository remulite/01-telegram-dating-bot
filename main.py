import telebot
import json
import os
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import TOKEN

bot = telebot.TeleBot(TOKEN)

# @bot.message_handler(commands=['start'])
# def start(message):
#     bot.send_message(message.chat.id, "Добро пожаловать!\n\nЗдесь можно найти новых людей.\n\n👇 Начнем создание анкеты?")

DATABASE_FILE = 'database.json'
user_data = {}
user_states = {}

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    keyboard.add(types.KeyboardButton('📋 Меню'))

    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton(
        '📝 Создать анкету',
        callback_data='create_profile'
    )
    markup.add(button)

    bot.send_message(
        message.chat.id,
        'Добро пожаловать!\\n\\nЗдесь можно найти новых людей.\\n\\n👇 Начнем создание анкеты?',
        reply_markup=keyboard
    )

    bot.send_message(
        message.chat.id,
        'Или создайте анкету:',
        reply_markup=markup
    )



def set_state(user_id, state):
    user_states[user_id] = state

def get_state(user_id):
    return user_states.get(user_id)

def clear_state(user_id):
    user_states.pop(user_id, None)


def load_database():
    if not os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=4)

    with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_database(user_id):
    db = load_database()
    db[str(user_id)] = user_data[user_id]

    with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)


def start_keyboard():
    kb = InlineKeyboardMarkup()

    kb.add(
        InlineKeyboardButton(
            '📝 Создать анкету',
            callback_data='create_profile'
        )
    )

    return kb


def gender_keyboard():
    kb = InlineKeyboardMarkup()

    kb.row(
        InlineKeyboardButton('👨 Парень', callback_data='male'),
        InlineKeyboardButton('👩 Девушка', callback_data='female')
    )

    return kb


@bot.callback_query_handler(func=lambda call: call.data == 'create_profile')
def profile(call):
    user_id = call.from_user.id

    user_data[user_id] = {}

    set_state(user_id, 'waiting_name')

    bot.send_message(
        call.message.chat.id,
        'Давайте создадим вашу анкету!\\n\\nКак вас зовут?'
    )



@bot.message_handler(func=lambda m: get_state(m.from_user.id) == 'waiting_name')
def getname(message):
    name = message.text.strip()

    if not name:
        bot.send_message(message.chat.id, 'Имя не должно быть пустым.')
        return

    user_data[message.from_user.id]['name'] = name

    set_state(message.from_user.id, 'waiting_age')

    bot.send_message(
        message.chat.id,
        'Сколько вам лет?'
    )


@bot.message_handler(func=lambda m: get_state(m.from_user.id) == 'waiting_age')
def getage(message):
    if not message.text.isdigit():
        bot.send_message(message.chat.id, 'Введите корректный возраст.')
        return

    age = int(message.text)

    if age < 14 or age > 99:
        bot.send_message(message.chat.id, 'Введите корректный возраст.')
        return

    user_data[message.from_user.id]['age'] = age

    set_state(message.from_user.id, 'waiting_gender')

    bot.send_message(
        message.chat.id,
        'Ваш пол?',
        reply_markup=gender_keyboard()
    )


@bot.callback_query_handler(func=lambda call: get_state(call.from_user.id) == 'waiting_gender')
def gender(call):
    gender = 'Парень'

    if call.data == 'female':
        gender = 'Девушка'

    user_data[call.from_user.id]['gender'] = gender

    set_state(call.from_user.id, 'waiting_photo')

    bot.send_message(
        call.message.chat.id,
        'Отправьте одну фотографию для анкеты.'
    )


@bot.message_handler(content_types=['photo'])
def getphoto(message):
    if get_state(message.from_user.id) != 'waiting_photo':
        return

    file_id = message.photo[-1].file_id

    user_data[message.from_user.id]['photo'] = file_id

    save_database(message.from_user.id)

    data = user_data[message.from_user.id]

    caption = (
        '✅ Анкета готова!\\n\\n'
        f'Имя: {data["name"]}\\n'
        f'Возраст: {data["age"]}\\n'
        f'Пол: {data["gender"]}\\n\\n'
        'Теперь вы можете начать поиск собеседников.'
    )

    bot.send_message(
        message.chat.id,
        'Анкета успешно создана!'
    )

    bot.send_photo(
        message.chat.id,
        file_id,
        caption=caption
    )

    clear_state(message.from_user.id)


@bot.message_handler(func=lambda m: get_state(m.from_user.id) == 'waiting_photo')
def wrongphoto(message):
    bot.send_message(
        message.chat.id,
        'Пожалуйста, отправьте фотографию.'
    )


@bot.message_handler(func=lambda m: m.text == '📋 Меню')
def menu(message):
    bot.send_message(
        message.chat.id,
        '📋 Пока здесь ничего нет.'
    )

print('Бот запущен:)')

bot.infinity_polling(skip_pending=True)