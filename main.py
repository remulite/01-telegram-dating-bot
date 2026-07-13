import telebot
from telebot import types
from config import TOKEN

bot = telebot.TeleBot(TOKEN)

# @bot.message_handler(commands=['start'])
# def start(message):
#     bot.send_message(message.chat.id, "Добро пожаловать!\n\nЗдесь можно найти новых людей.\n\n👇 Начнем создание анкеты?")

user_data = {}

@bot.message_handler(commands=['start'])
def start(messaage):
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("📝 Создать анкету", callback_data="create_profile")
    markup.add(button)

    bot.send_message(messaage.chat.id, "Добро пожаловать!\n\nЗдесь можно найти новых людей.\n\n👇 Начнем создание анкеты?", reply_markup=markup)



bot.polling(none_stop=True)