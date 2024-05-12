from aiogram import Router, F
from aiogram.fsm.storage.memory import MemoryStorage, StorageKey
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiohttp import ClientSession

from backend.src.schemas.user_schema import UserUpdate
from backend.src.tg_bot.constants import *

rtr = Router()
token_storage = MemoryStorage()


class Registration(StatesGroup):
    full_name = State()
    email = State()
    password = State()
    phone_number = State()
    telegram_id = State()
    plate = State()


class Token(StatesGroup):
    token = State()


async def login(data: dict, message: Message):
    async with ClientSession(HOST) as session:
        async with session.post(
                f"/api/auth/login",
                data={"username": data.get("phone_number"), "password": data.get("password")},
        ) as response:
            if response.status == 200:
                json_response = await response.json()
            else:
                await message.answer(TRY_AGAIN)
                return
        bearer = json_response.get("access_token")
        await token_storage.set_data(StorageKey(
            bot_id=message.bot.id, chat_id=message.chat.id, user_id=message.from_user.id
        ), {"id": data.get("id")})
        await token_storage.set_data(StorageKey(
            bot_id=message.bot.id, chat_id=message.chat.id, user_id=message.from_user.id
        ), {"access_token": bearer})
        if not data.get("telegram_id"):
            updated_user = UserUpdate(email=data.get("email"), telegram_id=message.from_user.id)
            async with session.patch(
                    f"/api/users/me",
                    json=updated_user.dict(exclude_none=True),
                    headers={"Authorization": f"Bearer {bearer}"}
            ):
                pass
    await message.answer(LOGIN, reply_markup=KB_REGISTERED)


@rtr.message(F.contact)
async def get_user(message: Message, state: FSMContext):
    async with ClientSession(HOST) as session:
        async with session.get(
                f"/api/telegram/user/{message.contact.user_id}/{message.contact.phone_number}"
        ) as response:
            if response.status == 200:
                json_response = await response.json()
                await state.update_data(**json_response)
                await state.set_state(Registration.password)
                await message.answer(GO_LOGIN)
                await message.answer(PASSWORD)
            elif response.status == 404:
                data = {
                    "phone_number": message.contact.phone_number,
                    "telegram_id": message.contact.user_id,
                }
                await state.update_data(**data)
                await state.set_state(Registration.full_name)
                await message.answer(FULLNAME)  # , reply_markup=KB_SITE)
            else:
                await message.answer(TRY_AGAIN, reply_markup=KB_SUPPORT)


@rtr.message(Registration.full_name)
async def get_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(Registration.email)
    await message.answer(EMAIL)


@rtr.message(Registration.email)
async def get_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await state.set_state(Registration.password)
    await message.answer(PASSWORD)


@rtr.message(Registration.password)
async def get_password(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    await message.delete()
    data = await state.get_data()
    user_id = data.get("id")
    if user_id:
        await login(data, message)
    else:
        async with ClientSession(HOST) as session:
            await session.post('/api/auth/signup', json=data)
        await state.clear()
        await message.answer(REGISTERED, reply_markup=KB_REGISTERED)
