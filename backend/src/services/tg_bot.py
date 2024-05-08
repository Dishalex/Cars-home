import asyncio

from aiogram import Bot, Dispatcher
from aiogram.methods import DeleteWebhook
from aiogram.types import *

from backend.src import config
from .constants import *
from .filters import Admin
from .handlers import rt

# bot = Bot(config.TG_TOKEN)
# dp = Dispatcher()
# dp.include_router(rt)
#
#
# async def main():
#     await bot(DeleteWebhook(drop_pending_updates=True))
#     if Admin():
#         await bot.set_my_commands([BotCommand(command=command[0], description=command[1]) for command in ADM_COMMANDS])
#     else:
#         await bot.set_my_commands([BotCommand(command=command[0], description=command[1]) for command in USR_COMMANDS])
#     try:
#         await dp.start_polling(bot)
#     finally:
#         await bot.session.close()
#
#
# if __name__ == '__main__':
#     asyncio.run(main())
