from aiogram.filters import Filter
from aiogram.types import Message

from src.conf.config import config


class Admin(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in config.ADMINS.values()
