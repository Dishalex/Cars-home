from backend.src import bot

from backend.src.services.constants import NOTIFICATIONS


async def notification(user_id, option):
    text = NOTIFICATIONS.get(option).get("message")
    markup = NOTIFICATIONS.get(option).get("reply_markup")
    if text:
        await bot.send_message(user_id, text, reply_markup=markup)
