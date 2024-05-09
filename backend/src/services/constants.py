from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

HOST = "http://localhost:8000"
USR_COMMANDS = {
    "show": {
        "name": "Показати авто",
        "description": "Список твоїх авто і інформація про них",
        "url": "api/admin/cars",
    },
    "add": {
        "name": "Додати авто",
        "description": "Додає нове авто в твій список",
        "url": "api/admin/cars",
    },
    "history": {"name": "Історія", "description": "Ціни і час паркування", "url": ""},
    "help": {"name": "Інструкція"},
}

ADM_COMMANDS = {
    **USR_COMMANDS,
    "settings": {"name": "Налаштування"},
    "Id": {"name": "Ваш ІД"},
}
command_list = "\n".join(
    [f"* {command} - {info.get('name')}" for command, info in USR_COMMANDS.items()]
)[:-1]

KB_START = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Поділитись номером", request_contact=True)],
    ],
    one_time_keyboard=True,
    input_field_placeholder="Більше можливостей після реєстріції",
)
KB_REGISTERED = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Мої авто", callback_data="cars")
        ]
    ]
)
KB_HELP = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=command, callback_data=info.get("name"))
            for command, info in USR_COMMANDS.items()
        ][:-1]
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

START = "Почнімо з реєстрації. Тисни <b>/Поділитись номером</b> внизу. Або тисни <b>/help</b> щоб дізнатись можливості."
REGISTERED = "Ви зареєстровані! Можете подивитись дані про свої авто"
FULLNAME = "Введіть своє ім'я"
EMAIL = "Введіть свій email"
PASSWORD = "Введіть свій пароль"
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
