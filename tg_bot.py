import os
import telebot
from telebot import types
from dotenv import load_dotenv
import base64
from flask import Flask
import threading
import signal


load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")


bot = telebot.TeleBot(TOKEN)

# Ініціалізація Flask
app = Flask(__name__)

admin_id = base64.b64decode('OTQ2MjY4NDk2').decode('utf-8')

@app.route('/')
def index():
    return 'Бот працює'

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup()
    item1 = types.KeyboardButton('Розпочати')
    markup.row(item1)
    bot.send_message(message.chat.id, "Натисніть кнопку, щоб розпочати", reply_markup=markup)
@app.route('/')

@bot.message_handler(func=lambda message: message.text == 'Розпочати')
def start_message(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='telegram', callback_data='telegram')
    markup.row(btn1)
    bot.send_message(message.chat.id, 
        f"Привіт, {message.from_user.first_name}! "
        f"Я бот, який допоможе зв'язатися з адміністратором. "
        f"Тицяй на telegram, і тобі допоможуть у вирішенні труднощів", 
        reply_markup=markup)

@bot.callback_query_handler(func=lambda _: True)
def callback_message(callback):
    if callback.data == 'telegram':
        bot.send_message(callback.message.chat.id, 
            'Надішли повідомлення, воно надійде адміністратору в Telegram. Очікуйте відповіді.')

@bot.message_handler(func=lambda _: True)
def message_handler(callback):
    try:
        if callback.text:
            username = callback.from_user.username
            if username is None:
                bot.send_message(callback.chat.id, 
                    "У вас не вказаний нікнейм. Спробуйте виправити це та повернутися до бота.")
                return
                
            bot.send_message(admin_id, 
                f"Повідомлення в телеграм боті \"{bot.get_me().first_name}\" "
                f"від користувача \"{callback.from_user.first_name} (@{username})\": \n\n{callback.text}")
            bot.send_message(callback.chat.id, 'Повідомлення надійшло адміністратору. Очікуйте відповіді.')
        else:
            bot.send_message(callback.chat.id, 'Повідомлення не надійшло. Спробуйте ще раз.')
    except Exception as e:
        bot.send_message(callback.chat.id, 'Виникла помилка при обробці повідомлення. Спробуйте пізніше.')
        print(f"Error in message_handler: {e}")

def signal_handler(_, __):
    print('Зупинка бота...')
    bot.stop_polling()
    exit(0)

def run_flask():
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Запуск бота
    print('Запуск бота...')
    bot.infinity_polling()
