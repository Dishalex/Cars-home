from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import *

from .constants import *

rt = Router()


@rt.message(CommandStart())
async def starting(message: Message):
    await message.answer(START, 'HTML')


@rt.message(Command('help'))
async def help_command(message: Message):
    await message.answer(HELP, 'HTML', reply_markup=KB_HELP)


@rt.message(Command('show'))
async def show(message: Message):
    pass


@rt.message(Command('add'))
async def add(message: Message):
    pass


@rt.message(Command('remove'))
async def remove(message: Message):
    pass


@rt.message(Command('history'))
async def history(message: Message):
    pass


@rt.message(Command('settings'))
async def settings(message: Message):
    pass


@rt.message(Command('Id'))
async def get_id(message: Message):
    if message.reply_to_message and message.reply_to_message.contact:
        await message.reply(
            f"{message.reply_to_message.contact.first_name}'s ID: {message.reply_to_message.contact.user_id}."
        )
    elif message.reply_to_message:
        await message.reply(
            f"{message.reply_to_message.from_user.first_name}'s  ID: {message.reply_to_message.from_user.id}."
        )
    else:
        await message.reply(
            f"Hello {message.from_user.first_name}! Your ID: {message.from_user.id}."
        )
