from tg_bot.constants import NOTIFICATIONS
from tg_bot.tg_bot import bot


async def notification(user_id, option):
    text = NOTIFICATIONS.get(option).get("message")
    markup = NOTIFICATIONS.get(option).get("reply_markup")
    if text:
        await bot.send_message(user_id, text, reply_markup=markup)
