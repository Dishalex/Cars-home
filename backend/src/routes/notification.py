from aiohttp import ClientSession

from backend.src.conf.config import config
from backend.src.entity.models import User

NOTIFICATIONS = {
    "in": {"text": "Авто прибуло в парк. Якщо це помилка, зверніться до підтримки"},
    "out": {"text": "Авто покинуло парк. Якщо це помилка, зверніться до підтримки"},
    "limit": {"text": "Час оплатити парковку"},
    "ban": {"text": "Ваше авто в чорному списку. Дізнатись більше - зверніться до підтримки"},
}

# INSTRUCTION!!!
# after your code put "await telegram_notification(<option>, user)"


async def telegram_notification(option: str, user: User):
    if user.telegram_id:
        url = f"https://api.telegram.org/bot{config.TG_TOKEN}/sendMessage"
        text = NOTIFICATIONS.get(option).get("text")
        params = {"chat_id": user.telegram_id, "text": text}
        async with ClientSession() as session:
            async with session.post(url, params=params) as response:
                pass
