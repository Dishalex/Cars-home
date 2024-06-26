from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

# HOST = "https://cars-home-app-private-student-cf52bc9b.koyeb.app"
HOST = "http://127.0.0.1:8000"
USR_COMMANDS = {
    "show": {
        "name": "Показати авто",
        "description": "Список твоїх авто і інформація про них",
        "url": "/api/users/cars",
    },
    "free": {
        "name": "Вільні місця",
        "description": "Кількість вільних місць",
        "url": "/api/admin/default-parking-rate",
    },
    "history": {
        "name": "Історія",
        "description": "Ціни і час паркування",
        "url": "/api/history/get_all_entries_by_period",
    },
    "help": {"name": "Інструкція"},
}
ADM_COMMANDS = {
    **USR_COMMANDS,
    "settings": {"name": "Налаштування"},
    "id": {"name": "Ваш ІД"},
}
command_list = "\n".join(
    [f"* {command} - {info.get('name')}" for command, info in USR_COMMANDS.items()][:-1]
)


class KeyboardButtons:
    KB_START = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Поділитись номером", request_contact=True)],
        ],
        one_time_keyboard=True,
        resize_keyboard=True,
        input_field_placeholder="Більше можливостей після реєстріції",
    )
    KB_REGISTERED = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Мої авто", callback_data="cars")]]
    )
    KB_HELP = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=command, callback_data=f"{command}_info")
                for command in USR_COMMANDS
            ][:-1]
        ]
    )
    KB_LIMIT = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Поповнити картку", callback_data="limit"),
            ]
        ]
    )
    KB_SUPPORT = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Підтримка", callback_data="support"),
            ]
        ]
    )


class InfoMessages:
    START = (
        "Почнімо з реєстрації. Тисни <b>Поділитись номером</b> внизу. "
        "Або тисни <b>/help</b> щоб дізнатись можливості."
    )
    TRY_AGAIN = "Сервіс не доступний. Спробуй пізніше"
    REGISTERED = "Ви зареєстровані! Можете подивитись дані про свої авто"
    GO_LOGIN = "Ви зареєстровані! Авторизуйтесь для доступу до ваших даних"
    LOGIN = "Вхід виконано успішно"
    FULLNAME = "Введіть своє ім'я"
    EMAIL = "Введіть свій email"
    PASSWORD = "Введіть свій пароль"
    UNAUTHORIZED = "Будь ласка, авторизуйтесь"
    FORBIDDEN = "Ваш акаунт заблоковано"
    NOT_FOUND = "Не знайдено"
    HELP = (
        "Тут ви можете отримати інформацію про всі команди\n\n"
        "<b>Зараз доступні такі команди:</b>\n"
        f"<b>{command_list}</b>\n\n"
        "Про яку команду тобі розповісти?"
    )
