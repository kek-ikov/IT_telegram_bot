!pip install python-telegram-bot==13.7

import os
import random
import re
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

TOKEN = '7852193453:AAFG0_6Ue65oAc0XF8cvjsTYbls7RHfGVGg'

# Пути к папкам
TEXTS_FOLDER = '/content/drive/MyDrive/IT_bot/texts'
IMAGES_FOLDER = '/content/drive/MyDrive/IT_bot/images'

# Состояния разговора для управления состоянием бота
MENU, TITLE_SEARCH, WORD_SEARCH = range(3)

# Флаг для отслеживания первого запуска бота
first_run = True


# Функция для начала разговора
def start(update: Update, context: CallbackContext) -> int:
    global first_run  # Используем глобальный флаг

    # Проверяем, был ли бот запущен впервые
    if first_run:
        # Отправляем приветственное сообщение пользователю
        update.message.reply_text(
            "Добро пожаловать! Этот бот поможет вам найти произведения писателя Артура Конан Дойла, который показал всему миру легендарного сыщика Шерлока Холмса."
        )
        first_run = False  # Устанавливаем флаг в False после первого запуска

    # Создаем клавиатуру с опциями для пользователя
    keyboard = [['О чат-боте', 'Поиск произведения по названию', 'Поиск произведения по словам']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    # Отправляем сообщение с просьбой выбрать опцию из меню
    update.message.reply_text("Выберите опцию:", reply_markup=reply_markup)

    return MENU  # Переходим в состояние MENU


# Функция для обработки выбора в меню
def menu_choice(update: Update, context: CallbackContext) -> int:
    choice = update.message.text  # Получаем текст сообщения от пользователя

    # Обрабатываем выбор пользователя
    if choice == 'О чат-боте':
        update.message.reply_text(
            "Этот бот разработан студентом Клепиковым Кириллом (известным под псевдонимом kiri4) и служит для поиска произведений писателя Артура Конан Дойла.")
        return start(update, context)  # Возвращаемся в главное меню
    elif choice == 'Поиск произведения по названию':
        update.message.reply_text("Введите название произведения:", reply_markup=ReplyKeyboardRemove())
        return TITLE_SEARCH  # Переходим в состояние TITLE_SEARCH
    elif choice == 'Поиск произведения по словам':
        update.message.reply_text("Введите слово для поиска:", reply_markup=ReplyKeyboardRemove())
        return WORD_SEARCH  # Переходим в состояние WORD_SEARCH


# Функция для поиска произведения по названию
def search_by_title(update: Update, context: CallbackContext) -> int:
    title = update.message.text  # Получаем название произведения от пользователя

    # Ищем файл с указанным названием в папке текстов
    for filename in os.listdir(TEXTS_FOLDER):
        if filename.lower().startswith(title.lower()):  # Сравниваем названия без учета регистра
            with open(os.path.join(TEXTS_FOLDER, filename), 'r', encoding='utf-8') as file:
                content = file.read()  # Читаем содержимое файла
                fragment = ' '.join(content.split()[:30]) + '...'  # Берем первые 30 слов

            # Проверяем наличие изображения обложки книги
            image_path = os.path.join(IMAGES_FOLDER, filename.replace('.txt', '.jpg'))
            if os.path.exists(image_path):
                update.message.reply_photo(photo=open(image_path, 'rb'),
                                           caption=fragment)  # Отправляем изображение и фрагмент текста
            else:
                # Если изображения нет, отправляем изображение писателя
                author_image = random.choice([img for img in os.listdir(IMAGES_FOLDER) if img.startswith('author')])
                update.message.reply_photo(photo=open(os.path.join(IMAGES_FOLDER, author_image), 'rb'),
                                           caption=fragment)

            return start(update, context)  # Возвращаемся в главное меню

    update.message.reply_text("Произведение не найдено.")  # Если произведение не найдено
    return start(update, context)


# Функция для поиска произведения по словам
def search_by_word(update: Update, context: CallbackContext) -> int:
    word = update.message.text.lower()  # Получаем слово от пользователя и переводим в нижний регистр
    found_works = []  # Список для хранения найденных произведений

    # Ищем слово в каждом файле текстов
    for filename in os.listdir(TEXTS_FOLDER):
        with open(os.path.join(TEXTS_FOLDER, filename), 'r', encoding='utf-8') as file:
            content = file.read().lower()  # Читаем содержимое файла и переводим в нижний регистр
            if re.search(r'\b' + re.escape(word) + r'\b', content):  # Проверяем наличие слова в тексте
                found_works.append(filename.replace('.txt', ''))  # Добавляем название произведения в список

    if found_works:
        response = "Произведения, содержащие слово '{}':\n".format(word)
        response += "\n".join(found_works)  # Формируем ответ с найденными произведениями
    else:
        response = "Произведения, содержащие слово '{}', не найдены.".format(word)

    update.message.reply_text(response)  # Отправляем ответ пользователю
    return start(update, context)  # Возвращаемся в главное меню


# Основная функция для запуска бота
def main() -> None:
    updater = Updater(TOKEN)  # Создаем объект Updater с токеном бота
    dp = updater.dispatcher  # Получаем диспетчер для обработки сообщений

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],  # Обрабатываем команду /start для начала разговора
        states={
            MENU: [MessageHandler(
                Filters.regex('^(О чат-боте|Поиск произведения по названию|Поиск произведения по словам)$'),
                menu_choice)],
            TITLE_SEARCH: [MessageHandler(Filters.text & ~Filters.command, search_by_title)],
            WORD_SEARCH: [MessageHandler(Filters.text & ~Filters.command, search_by_word)],
        },
        fallbacks=[CommandHandler('start', start)],  # Обработка команды /start как запасной вариант
    )

    dp.add_handler(conv_handler)  # Добавляем обработчик разговоров к диспетчеру
    updater.start_polling()  # Запускаем бота на прослушивание сообщений
    updater.idle()  # Ожидаем завершения работы


if __name__ == '__main__':
    main()  # Запускаем основную функцию при выполнении скрипта