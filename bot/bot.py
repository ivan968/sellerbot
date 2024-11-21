import os
import time
import threading
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Токен бота
TOKEN = os.environ['TOKEN']

# Глобальные переменные
enabled = False  # Включен ли бот для отправки сообщений
chats = []  # Список чатов для отправки сообщений
message_file = "message.txt"  # Файл с текстом сообщения


def read_message_from_file():
    """Читает текст из файла."""
    if os.path.exists(message_file):
        with open(message_file, 'r', encoding='utf-8') as file:
            return file.read().strip()
    return "Сообщение не задано. Измените файл message.txt."


def start(update: Update, context: CallbackContext):
    """Включает рассылку."""
    global enabled
    enabled = True
    update.message.reply_text("Рассылка включена. Сообщения будут отправляться каждые 15 секунд.")


def stop(update: Update, context: CallbackContext):
    """Останавливает рассылку."""
    global enabled
    enabled = False
    update.message.reply_text("Рассылка остановлена.")


def add_chat(update: Update, context: CallbackContext):
    # Новая версия функции
    if context.args:  # Если аргументы переданы
        try:
            chat_id = int(context.args[0])  # Преобразуем первый аргумент в число
            if chat_id not in chats:
                chats.append(chat_id)
                update.message.reply_text(f"Чат {chat_id} добавлен для отправки сообщений.")
            else:
                update.message.reply_text("Этот чат уже добавлен.")
        except ValueError:
            update.message.reply_text("Ошибка: ID чата должен быть числом.")
    else:  # Если аргументы не переданы, используем текущий чат
        chat_id = update.effective_chat.id
        if chat_id not in chats:
            chats.append(chat_id)
            update.message.reply_text(f"Текущий чат {chat_id} добавлен для отправки сообщений.")
        else:
            update.message.reply_text("Этот чат уже добавлен.")


def remove_chat(update: Update, context: CallbackContext):
    """Удаляет текущий чат из списка."""
    chat_id = update.effective_chat.id
    if chat_id in chats:
        chats.remove(chat_id)
        update.message.reply_text(f"Чат {chat_id} удален из списка рассылки.")
    else:
        update.message.reply_text("Чат не был добавлен в список.")


def list_chats(update: Update, context: CallbackContext):
    """Выводит список чатов для рассылки."""
    if chats:
        chat_list = "\n".join([str(chat) for chat in chats])
        update.message.reply_text(f"Список чатов для рассылки:\n{chat_list}")
    else:
        update.message.reply_text("Список чатов пуст.")


def send_messages():
    """Фоновая функция для отправки сообщений в выбранные чаты."""
    global enabled
    bot = Bot(TOKEN)
    while True:
        if enabled and chats:
            message = read_message_from_file()
            for chat_id in chats:
                try:
                    bot.send_message(chat_id, message)
                except Exception as e:
                    print(f"Ошибка при отправке в чат {chat_id}: {e}")
        time.sleep(15)


if __name__ == "__main__":
    # Поток для отправки сообщений
    threading.Thread(target=send_messages, daemon=True).start()

    # Настройка бота
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Команды
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("stop", stop))
    dispatcher.add_handler(CommandHandler("add_chat", add_chat, pass_args=True))
    dispatcher.add_handler(CommandHandler("remove_chat", remove_chat))
    dispatcher.add_handler(CommandHandler("list_chats", list_chats))

    # Запуск бота
    updater.start_polling()
    updater.idle()
