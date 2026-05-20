"""
Этап 2: Telegram-бот для изучения программирования
Использует pyTelegramBotAPI + сохраняет все запросы в Django БД
"""

import telebot
import random
import sys
import os
from pathlib import Path
from telebot import types

# Путь к корню проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Добавляем Django-проект в путь для импорта моделей
sys.path.insert(0, str(BASE_DIR / "admin_panel"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "admin_panel.settings")

import django
django.setup()

from queries.models import UserQuery


BOT_TOKEN = " "

bot = telebot.TeleBot(BOT_TOKEN)

QUOTES_FILE = BASE_DIR / "quotes.txt"

# ──────────────────────────────────────────────
# Данные: темы, примеры, задания, вопросы
# ──────────────────────────────────────────────

topics = {
    "переменные": "Переменные нужны для хранения данных. Пример: name = 'Ali', age = 15.",
    "типы данных": "Основные типы данных в Python: int, float, str, bool, list, dict.",
    "условия": "Условия позволяют выполнять код в зависимости от проверки. Пример: if x > 0:",
    "циклы": "Циклы помогают повторять действия. В Python есть for и while.",
    "функции": "Функции — это именованные блоки кода. Пример: def hello():",
    "списки": "Список хранит несколько значений. Пример: numbers = [1, 2, 3].",
    "словари": "Словарь хранит пары ключ-значение. Пример: student = {'name': 'Aruzhan'}.",
    "строки": "Строка — это текст. Пример: text = 'Привет'.",
    "ввод и вывод": "Для ввода используется input(), для вывода — print().",
    "операторы": "Операторы нужны для вычислений и сравнений: +, -, *, /, ==, >, <.",
}

examples = {
    "переменные": 'name = "Муслим"\nage = 18\nprint(name)\nprint(age)',
    "типы данных": 'x = 10\ny = 3.14\nname = "Ali"\nis_ok = True\nprint(type(x))\nprint(type(name))',
    "условия": 'age = 18\nif age >= 18:\n    print("Доступ разрешен")\nelse:\n    print("Доступ запрещен")',
    "циклы": "for i in range(1, 6):\n    print(i)",
    "функции": 'def greet(name):\n    print("Привет,", name)\ngreet("Алия")',
    "списки": "numbers = [10, 20, 30, 40]\nprint(numbers[0])\nprint(numbers[-1])",
    "словари": 'student = {\n    "name": "Arman",\n    "age": 14\n}\nprint(student["name"])',
    "строки": 'text = "Python"\nprint(text.upper())\nprint(len(text))',
    "ввод и вывод": 'name = input("Введите имя: ")\nprint("Привет,", name)',
    "операторы": "a = 10\nb = 3\nprint(a + b)\nprint(a > b)\nprint(a == b)",
}

tasks = {
    "переменные": "Создай переменные name и age. Запиши в них своё имя и возраст, затем выведи их.",
    "типы данных": "Создай по одной переменной типов int, float, str и bool. Выведи их типы через type().",
    "условия": "Напиши программу, которая проверяет: число положительное, отрицательное или равно нулю.",
    "циклы": "С помощью цикла for выведи числа от 1 до 10.",
    "функции": "Создай функцию, которая принимает имя и выводит приветствие.",
    "списки": "Создай список из 5 чисел и выведи второй и последний элементы.",
    "словари": "Создай словарь с данными о книге: название, автор, год.",
    "строки": "Пусть есть строка с твоим именем. Выведи её в верхнем регистре и её длину.",
    "ввод и вывод": "Запроси у пользователя имя и возраст, а затем красиво выведи их.",
    "операторы": "Создай две переменные и выведи результаты сложения, умножения и сравнения.",
}

quiz_questions = [
    {"question": "Какая функция используется для вывода текста на экран?", "answer": "print"},
    {"question": "Какая функция используется для ввода данных с клавиатуры?", "answer": "input"},
    {"question": "Как называется тип данных для целых чисел?", "answer": "int"},
    {"question": "Какой оператор используется для сравнения на равенство?", "answer": "=="},
    {"question": "Как называется структура данных в квадратных скобках?", "answer": "список"},
]

# Хранение состояния викторины по user_id
quiz_state = {}


# ──────────────────────────────────────────────
# Вспомогательные функции для интерфейса
# ──────────────────────────────────────────────

def get_main_keyboard():
    """Создает постоянную клавиатуру главного меню (Reply)."""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_topics = types.KeyboardButton("📚 Темы")
    btn_quiz = types.KeyboardButton("🎯 Викторина")
    btn_quote = types.KeyboardButton("💬 Цитата")
    btn_progress = types.KeyboardButton("📊 Статистика")
    btn_help = types.KeyboardButton("📋 Помощь")
    
    markup.add(btn_topics, btn_quiz, btn_quote, btn_progress, btn_help)
    return markup


def get_topics_inline_keyboard(prefix: str):
    """Создает inline-кнопки под сообщением для выбора конкретной темы."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for topic in topics.keys():
        callback_data = f"{prefix}:{topic}"
        buttons.append(types.InlineKeyboardButton(text=topic.capitalize(), callback_data=callback_data))
    
    markup.add(*buttons)
    return markup


def load_quotes():
    try:
        with open(QUOTES_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            return lines if lines else ["Цитаты пока не добавлены."]
    except FileNotFoundError:
        return ["Файл quotes.txt не найден."]


def save_query(user_id: int, username: str, command: str, response: str):
    """Сохраняет запрос пользователя в Django БД."""
    try:
        UserQuery.objects.create(
            user_id=user_id,
            username=username or "anonymous",
            command=command,
            response=response,
        )
    except Exception as e:
        print(f"[DB ERROR] Не удалось сохранить запрос: {e}")


def get_username(message) -> str:
    return message.from_user.username or message.from_user.first_name or "anonymous"


# ──────────────────────────────────────────────
# Обработчики команд
# ──────────────────────────────────────────────

@bot.message_handler(commands=["start"])
def cmd_start(message):
    response = (
        "👋 Привет! Я чат-бот для изучения Python.\n\n"
        "Я могу:\n"
        "📚 Объяснять темы\n"
        "💻 Показывать примеры кода\n"
        "✏️ Давать задания\n"
        "🎯 Проводить мини-викторины\n\n"
        "Используй меню внизу экрана или команду /help для навигации!"
    )
    bot.send_message(message.chat.id, response, reply_markup=get_main_keyboard())
    save_query(message.from_user.id, get_username(message), "/start", response)


@bot.message_handler(commands=["help"])
def cmd_help(message):
    response = (
        "📋 *Список команд:*\n\n"
        "/start — начать работу\n"
        "/help — список команд\n"
        "/topics — список доступных тем\n"
        "/topic [тема] — объяснение темы\n"
        "/example [тема] — пример кода\n"
        "/task [тема] — задание по теме\n"
        "/quiz — случайный вопрос викторины\n"
        "/quote — случайная цитата\n"
        "/weather [город] — погода (заглушка)\n"
        "/progress — статистика запросов"
    )
    bot.send_message(message.chat.id, response, parse_mode="Markdown", reply_markup=get_main_keyboard())
    save_query(message.from_user.id, get_username(message), "/help", response)


@bot.message_handler(commands=["topics"])
def cmd_topics(message):
    response = "📚 *Выберите интересующий вас раздел и тему:* "
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📖 Читать теорию", callback_data="menu:topic"),
        types.InlineKeyboardButton("💻 Смотреть пример кода", callback_data="menu:example"),
        types.InlineKeyboardButton("✏️ Получить задание", callback_data="menu:task")
    )
    
    bot.send_message(message.chat.id, response, parse_mode="Markdown", reply_markup=markup)
    save_query(message.from_user.id, get_username(message), "/topics", response)


@bot.message_handler(commands=["topic"])
def cmd_topic(message):
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        response = "⚠️ Выберите тему из списка ниже:"
        bot.send_message(message.chat.id, response, reply_markup=get_topics_inline_keyboard("show_topic"))
        save_query(message.from_user.id, get_username(message), message.text, response)
        return

    topic_name = parts[1].lower()
    if topic_name in topics:
        response = f"📖 *Тема: {topic_name}*\n\n{topics[topic_name]}"
        bot.send_message(message.chat.id, response, parse_mode="Markdown")
    else:
        available = ", ".join(topics.keys())
        response = f"❌ Тема «{topic_name}» не найдена.\n\nДоступные темы: {available}"
        bot.send_message(message.chat.id, response)

    save_query(message.from_user.id, get_username(message), message.text, response)


@bot.message_handler(commands=["example"])
def cmd_example(message):
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        response = "⚠️ Выберите тему для вывода примера кода:"
        bot.send_message(message.chat.id, response, reply_markup=get_topics_inline_keyboard("show_example"))
        save_query(message.from_user.id, get_username(message), message.text, response)
        return

    topic_name = parts[1].lower()
    if topic_name in examples:
        response = f"💻 *Пример по теме «{topic_name}»:*\n\n```python\n{examples[topic_name]}\n```"
        bot.send_message(message.chat.id, response, parse_mode="Markdown")
    else:
        response = f"❌ Пример для темы «{topic_name}» не найден."
        bot.send_message(message.chat.id, response)

    save_query(message.from_user.id, get_username(message), message.text, response)


@bot.message_handler(commands=["task"])
def cmd_task(message):
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        response = "⚠️ Выберите тему для получения практического задания:"
        bot.send_message(message.chat.id, response, reply_markup=get_topics_inline_keyboard("show_task"))
        save_query(message.from_user.id, get_username(message), message.text, response)
        return

    topic_name = parts[1].lower()
    if topic_name in tasks:
        response = f"✏️ *Задание по теме «{topic_name}»:*\n\n{tasks[topic_name]}"
        bot.send_message(message.chat.id, response, parse_mode="Markdown")
    else:
        response = f"❌ Задание для темы «{topic_name}» не найдено."
        bot.send_message(message.chat.id, response)

    save_query(message.from_user.id, get_username(message), message.text, response)


@bot.message_handler(commands=["quiz"])
def cmd_quiz(message):
    q = random.choice(quiz_questions)
    quiz_state[message.from_user.id] = q["answer"]
    response = f"🎯 *Вопрос викторины:*\n\n{q['question']}\n\nВведи ответ в чат:"
    bot.send_message(message.chat.id, response, parse_mode="Markdown", reply_markup=types.ReplyKeyboardRemove())
    save_query(message.from_user.id, get_username(message), "/quiz", q["question"])


@bot.message_handler(commands=["quote"])
def cmd_quote(message):
    quote = random.choice(load_quotes())
    response = f"💬 {quote}"
    bot.send_message(message.chat.id, response)
    save_query(message.from_user.id, get_username(message), "/quote", response)


@bot.message_handler(commands=["weather"])
def cmd_weather(message):
    parts = message.text.strip().split(maxsplit=1)
    # Защита ТЗ пункт 5: обработка пустого ввода города
    if len(parts) > 1:
        city = parts[1].strip()
    else:
        city = "Алматы"  # Значение по умолчанию, если город не передан
        
    response = (
        f"🌤 *Погода в городе {city}:*\n\n"
        f"🌡 Температура: +22°C\n"
        f"💨 Ветер: 5 м/с\n"
        f"☁️ Облачность: 30%\n\n"
        f"_(Это заглушка. Подключи реальный API погоды для настоящих данных.)_"
    )
    bot.send_message(message.chat.id, response, parse_mode="Markdown")
    save_query(message.from_user.id, get_username(message), message.text, response)


@bot.message_handler(commands=["progress"])
def cmd_progress(message):
    user_id = message.from_user.id
    count = UserQuery.objects.filter(user_id=user_id).count()
    response = (
        f"📊 *Твоя статистика:*\n\n"
        f"Всего запросов: {count}"
    )
    bot.send_message(message.chat.id, response, parse_mode="Markdown")
    save_query(message.from_user.id, get_username(message), "/progress", response)


# ──────────────────────────────────────────────
# Обработчик нажатий Inline-кнопок (с защитой try-except)
# ──────────────────────────────────────────────

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    """Обрабатывает клики по inline-кнопкам под сообщениями."""
    try:
        user_id = call.from_user.id
        username = call.from_user.username or call.from_user.first_name or "anonymous"
        
        # 1. Выбор категории в /topics
        if call.data.startswith("menu:"):
            action = call.data.split(":")[1]
            if action == "topic":
                bot.edit_message_text("📖 Выберите тему теории:", call.message.chat.id, call.message.message_id, 
                                      reply_markup=get_topics_inline_keyboard("show_topic"))
            elif action == "example":
                bot.edit_message_text("💻 Выберите тему для кода:", call.message.chat.id, call.message.message_id, 
                                      reply_markup=get_topics_inline_keyboard("show_example"))
            elif action == "task":
                bot.edit_message_text("✏️ Выберите тему для задачи:", call.message.chat.id, call.message.message_id, 
                                      reply_markup=get_topics_inline_keyboard("show_task"))
            return

        # 2. Выбор конкретной темы
        prefix, topic_name = call.data.split(":", 1)
        response = ""
        
        if prefix == "show_topic":
            response = f"📖 *Тема: {topic_name}*\n\n{topics[topic_name]}"
            bot.send_message(call.message.chat.id, response, parse_mode="Markdown")
        elif prefix == "show_example":
            response = f"💻 *Пример по теме «{topic_name}»:*\n\n```python\n{examples[topic_name]}\n```"
            bot.send_message(call.message.chat.id, response, parse_mode="Markdown")
        elif prefix == "show_task":
            response = f"✏️ *Задание по теме «{topic_name}»:*\n\n{tasks[topic_name]}"
            bot.send_message(call.message.chat.id, response, parse_mode="Markdown")
            
        bot.answer_callback_query(call.id)
        save_query(user_id, username, f"/[inline {prefix}] {topic_name}", response)
        
    except Exception as e:
        print(f"[ERROR] Ошибка обработки callback: {e}")
        bot.answer_callback_query(call.id, text="⚠️ Произошла ошибка. Повторите запрос.")


# ──────────────────────────────────────────────
# Обработчик обычного текста (викторина + Reply-меню)
# ──────────────────────────────────────────────

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    user_id = message.from_user.id
    text = message.text.strip()

    # Проверяем, ожидаем ли ответ на викторину
    if user_id in quiz_state:
        correct = quiz_state.pop(user_id)
        user_answer = text.lower()
        if user_answer == correct.lower():
            response = "✅ Верно! Молодец! 🎉"
        else:
            response = f"❌ Неверно. Правильный ответ: *{correct}*"
            
        bot.send_message(message.chat.id, response, parse_mode="Markdown", reply_markup=get_main_keyboard())
        save_query(user_id, get_username(message), f"[quiz answer] {message.text}", response)
        return

    # Перенаправляем текст с Reply-кнопок на функции команд
    if text == "📚 Темы":
        cmd_topics(message)
        return
    elif text == "🎯 Викторина":
        cmd_quiz(message)
        return
    elif text == "💬 Цитата":
        cmd_quote(message)
        return
    elif text == "📊 Статистика":
        cmd_progress(message)
        return
    elif text == "📋 Помощь":
        cmd_help(message)
        return

    # Неизвестное сообщение (ТЗ пункт 5)
    response = "❓ Не понял команду. Используй /help или меню для списка команд."
    bot.send_message(message.chat.id, response, reply_markup=get_main_keyboard())
    save_query(user_id, get_username(message), message.text, response)


# ──────────────────────────────────────────────
# Запуск
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("🤖 Бот запущен. Нажми Ctrl+C для остановки.")
    bot.infinity_polling()
