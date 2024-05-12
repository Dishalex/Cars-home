from aiogram.filters import Filter
from aiogram.types import Message

from backend.src.conf.config import config


class Admin(Filter):
    async def __call__(self, user_id: int) -> bool:
        return user_id in config.ADMINS.values()
