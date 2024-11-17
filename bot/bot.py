import os
import time
import threading
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Токен бота, берется из переменной окружения
TOKEN = os.environ['7855092388:AAHK7zy2jnXR110StjuuTmkoEaNobiIme3s']

# Глобальные переменные
enabled = False  # Указывает, включен ли бот для отправки сообщений
chats = []  # Список чатов для отправки сообщений
message_file = "message.txt"  # Файл с текстом сообщения


def read_message_from_file():
    """Читает сообщение из текстового файла."""
    if os.path.exists(message_file):
        with open(message_file, 'r', encoding='utf-8') as file:
            return file.read().strip()
    return "Текст сообщения не задан. Измените файл message.txt."


def start(update: Update, context: CallbackContext):
    """Команда /start включает отправку сообщений."""
    global enabled
    enabled = True
    update.message.reply_text("Бот включен и будет отправлять сообщения каждые 15 секунд!")


def stop(update: Update, context: CallbackContext):
    """Команда /stop останавливает отправку сообщений."""
    global enabled
    enabled = False
    update.message.reply_text("Бот остановлен.")


def add_chat(update: Update, context: CallbackContext):
    """Добавляет текущий чат в список."""
    chat_id = update.effective_chat.id
    if chat_id not in chats:
        chats.append(chat_id)
        update.message.reply_text(f"Чат {chat_id} добавлен для отправки сообщений.")
    else:
        update.message.reply_text("Этот чат уже добавлен.")


def remove_chat(update: Update, context: CallbackContext):
    """Удаляет текущий чат из списка."""
    chat_id = update.effective_chat.id
    if chat_id in chats:
        chats.remove(chat_id)
        update.message.reply_text(f"Чат {chat_id} удален из списка.")
    else:
        update.message.reply_text("Этот чат не был добавлен.")


def send_messages():
    """Функция для отправки сообщений каждые 15 секунд."""
    global enabled
    bot = Bot(TOKEN)
    while True:
        if enabled and chats:
            message = read_message_from_file()
            for chat_id in chats:
                try:
                    bot.send_message(chat_id, message)
                except Exception as e:
                    print(f"Ошибка отправки в чат {chat_id}: {e}")
        time.sleep(15)


if __name__ == "__main__":
    # Создаем поток для отправки сообщений
    threading.Thread(target=send_messages, daemon=True).start()

    # Создаем и запускаем бота
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Регистрация команд
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("stop", stop))
    dispatcher.add_handler(CommandHandler("add_chat", add_chat))
    dispatcher.add_handler(CommandHandler("remove_chat", remove_chat))

    # Запуск бота
    updater.start_polling()
    updater.idle()
