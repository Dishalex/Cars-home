from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


USR_COMMANDS = (
    ("show", "Показати авто", "Список твоїх авто і інформація про них."),
    ("add", "Додати авто", "Додає нове авто в твій список."),
    ("remove", "Видалити авто", "Видаляє авто з твого списку."),
    ("history", "Історія", "Ціни і час паркування."),
    ("help", "Інструкція"),
)

ADM_COMMANDS = USR_COMMANDS + (
    ("settings", "Налаштування"),
    ("Id", "Ваш ІД"),
)
command_list = "\n".join([f"- {command[0]}" for command in USR_COMMANDS[:-1]])

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
            InlineKeyboardButton(text="Поповнити картку"),
        ]
    ]
)
KB_SUPPORT = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Підтримка"),
        ]
    ]
)

START = "Почнімо з реєстрації. Або тисни <b>/help</b> щоб дізнатись можливості."
HELP = (
    "Тут ви можете отримати інформацію про всі команди\n\n"
    "<b>Зараз доступні такі команди:</b>\n"
    f"<b>{command_list}</b>\n\n"
    "Про яку команду тобі розповісти?"
)
NOTIFICATIONS = {
    "in": {
        "message": "Авто прибуло в парк. Якщо це помилка, зверніться до підтримки",
        "reply_markup": KB_SUPPORT,
    },
    "out": {
        "message": "Авто покинуло парк. Якщо це помилка, зверніться до підтримки",
        "reply_markup": KB_SUPPORT,
    },
    "limit": {"message": "Перевищено встановлені ліміти", "reply_markup": KB_LIMIT},
    "rate": {"message": "Тарифи змінено"},
    "ban": {
        "message": "Ваше авто в чорному списку. Дізнатись більше - зверніться до підтримки",
        "reply_markup": KB_SUPPORT,
    },
}
