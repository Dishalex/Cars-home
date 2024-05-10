import asyncio

from aiogram import Bot, Dispatcher
from aiogram.methods import DeleteWebhook
from aiogram.types import *

from backend.src.conf.config import config
from backend.src.services.constants import *
from backend.src.services.filters import Admin
from backend.src.services.handlers import rt
from backend.src.services.registration import rtr


async def main():
    bot = Bot(config.TG_TOKEN)
    dp = Dispatcher()
    dp.include_router(rt)
    dp.include_router(rtr)

    await bot(DeleteWebhook(drop_pending_updates=True))

    await bot.set_my_commands(
            [BotCommand(command=command, description=info.get("name")) for command, info in USR_COMMANDS.items()]
    )

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
