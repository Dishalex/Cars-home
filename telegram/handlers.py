from datetime import date

from aiogram import Router, F
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.fsm.storage.memory import StorageKey
from aiogram.types import *
from aiohttp import ClientSession

from telegram.constants import *
from telegram.registration import token_storage

rt = Router()


async def do_get(message: Message, url: str, token: str):
    async with ClientSession(HOST) as session:
        async with session.get(
                url,
                headers={"Authorization": f"Bearer {token}"},
        ) as response:
            match response.status:
                case 200:
                    json_response = await response.json()
                    await message.answer(json_response)
                case 401:
                    await message.answer(InfoMessages.UNAUTHORIZED)
                case 403:
                    await message.answer(InfoMessages.FORBIDDEN)
                case 404:
                    await message.answer(InfoMessages.NOT_FOUND)
                case _:
                    await message.answer(InfoMessages.TRY_AGAIN)


@rt.message(CommandStart())
async def starting(message: Message):
    await message.answer(InfoMessages.START, reply_markup=KeyboardButtons.KB_START)


@rt.message(Command('help'))
async def help_command(message: Message):
    await message.answer(InfoMessages.HELP, reply_markup=KeyboardButtons.KB_HELP)


@rt.message(Command('show'))
async def show(message: Message, command: CommandObject = 'show'):
    access_token = await token_storage.get_data(StorageKey(
        bot_id=message.bot.id, chat_id=message.chat.id, user_id=message.from_user.id
    ))
    url = f'{USR_COMMANDS.get(command.command).get("url")}/{access_token.get("id")}'
    await do_get(message, url, access_token.get("access_token"))


@rt.message(Command('free'))
async def free(message: Message, command: CommandObject):
    access_token = await token_storage.get_data(StorageKey(
        bot_id=message.bot.id, chat_id=message.chat.id, user_id=message.from_user.id
    ))
    url = f'{USR_COMMANDS.get(command.command).get("url")}'
    await do_get(message, url, access_token.get("access_token"))


@rt.message(Command('history'))
async def history(message: Message, command: CommandObject):
    access_token = await token_storage.get_data(StorageKey(
        bot_id=message.bot.id, chat_id=message.chat.id, user_id=message.from_user.id
    ))
    url = f'{USR_COMMANDS.get(command.command).get("url")}/2024-05-15/{date.today()}'
    await do_get(message, url, access_token.get("access_token"))


@rt.message(Command('settings'))
async def settings(message: Message):
    pass


@rt.message(Command('id'))
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


@rt.callback_query(F.data == "cars")
async def get_cars(callback: CallbackQuery):
    await show(callback.message)


@rt.callback_query(F.data.endswith("_info"))
async def get_info(callback: CallbackQuery):
    await callback.answer()
    info = callback.data.split("_")[0]
    await callback.message.answer(f'<b>{info}</b>: {USR_COMMANDS.get(info).get("description")}')
