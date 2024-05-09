from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import *

from backend.src.services.constants import *

rtr = Router()


class Registration(StatesGroup):
    full_name = State()
    email = State()
    password = State()
    phone_number = State()
    telegram_id = State()


@rtr.message(F.contact)
async def get_contact(message: Message, state: FSMContext):
    db = []
    if message.contact.phone_number in db:
        await message.answer(REGISTERED, reply_markup=KB_REGISTERED)
        return
    data = {
        "phone_number": message.contact.phone_number,
        "telegram_id": message.contact.user_id,
    }
    await state.update_data(**data)
    await state.set_state(Registration.full_name)
    await message.answer(FULLNAME)


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
    await message.edit_text('*' * 8)
    data = await state.get_data()
    await message.answer(REGISTERED, reply_markup=KB_REGISTERED)
