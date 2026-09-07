import os
from flask import Flask, request
from threading import Thread
from telebot import TeleBot
from dotenv import load_dotenv
from bot import Dispatcher

load_dotenv()
TOKEN = os.getenv("TOKEN")


app = Flask(__name__)

@app.route('/')
def index():
    return "Бот запущен"

# Запускаем бота в отдельном потоке
def run_bot():
    dispatcher = Dispatcher(TOKEN)
    dispatcher.start()

if __name__ == '__main__':
    # Запускаем бота в потоке
    Thread(target=run_bot).start()
    # Запускаем Flask-сервер
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))