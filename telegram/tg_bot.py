import asyncio

from aiogram import Bot, Dispatcher
from aiogram.methods import DeleteWebhook
from aiogram.types import *

from telegram.config import config
from telegram.constants import USR_COMMANDS
from telegram.handlers import rt
from telegram.registration import rtr

bot = Bot(config.TG_TOKEN)
dp = Dispatcher()
dp.include_router(rt)
dp.include_router(rtr)


# @dp.callback_query(F.data == "admin")
# async def starting(message: Message):
#     await bot.delete_my_commands()
#     admin = await Admin()(message.from_user.id)
#     if admin:
#         await bot.set_my_commands(
#             [BotCommand(command=command, description=info.get("name")) for command, info in ADM_COMMANDS.items()]
#         )
#     else:
#         await bot.set_my_commands(
#             [BotCommand(command=command, description=info.get("name")) for command, info in USR_COMMANDS.items()]
#         )
#     await message.answer(START, 'HTML', reply_markup=KB_START)


async def main():
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
