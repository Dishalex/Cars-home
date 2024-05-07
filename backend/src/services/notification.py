from backend.src import bot

from .constants import NOTIFICATIONS

async def notification(user, option):
    await bot.send_message(
        user.telegram,
        NOTIFICATIONS.get(option, "Notification not found").get(
            "message", "Message not found"
        ),
        reply_markup=None,
    )
