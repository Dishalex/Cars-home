from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


USR_COMMANDS = (
    ("show", "Показати авто"),
    ("add", "Додати авто"),
    ("remove", "Видалити авто"),
    ("history", "Історія"),
    ("help", "Інструкція"),
)

ADM_COMMANDS = USR_COMMANDS + (
    ("settings", "Налаштування"),
    ("Id", "Ваш ІД"),
)
command_list = "\n".join([f"- {comm[0]}" for comm in USR_COMMANDS[:-1]])

KB_HELP = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=command[0], callback_data=command[1])
            for command in USR_COMMANDS[:-1]
        ]
    ]
)
KB_LIMIT = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Поповнити картку", callback_data="limit"),
        ]
    ]
)
KB_BAN = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Підтримка", callback_data="ban"),
        ]
    ]
)

START = 'Привіт! Я помічник паркування. Тисни <b>"Старт"</b>, щоб почати.'
HELP = (
    "Тут ви можете отримати інформацію про всі команди\n\n"
    "<b>Зараз доступні такі команди:</b>\n"
    f"<b>{command_list}</b>\n\n"
    "Про яку команду тобі розповісти?"
)
NOTIFICATIONS = {
    "in": {"message": "Авто прибуло в парк"},
    "out": {"message": "Авто покинуло парк"},
    "limit": {"message": "Перевищено встановлені ліміти", "reply_markup": KB_LIMIT},
    "rate": {"message": "Тарифи змінено"},
    "ban": {"message": "Ваше авто в чорному списку", "reply_markup": KB_BAN},
}
