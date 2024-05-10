from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import *

# from backend.src.routes.user_routes import update_own_profile
# from backend.src.schemas.user_schema import UserUpdate
# from backend.src.repository.users import get_user_by_tg_or_number, update_user
from backend.src.tg_bot.constants import *

rtr = Router()


class Registration(StatesGroup):
    full_name = State()
    email = State()
    password = State()
    phone_number = State()
    telegram_id = State()
    plate = State()


# @rtr.message(F.contact)
# async def get_contact(message: Message, state: FSMContext):
#     user = await get_user_by_tg_or_number(message.contact.user_id)
#     if user:
#         if not user.telegram_id:
#             updated_user = UserUpdate(email=user.email, telegram_id=message.contact.user_id)
#             await update_own_profile(updated_user, user)  # TODO: do from request
#         await message.answer(REGISTERED, reply_markup=KB_REGISTERED)
#     else:
#         data = {
#             "phone_number": message.contact.phone_number,
#             "telegram_id": message.contact.user_id,
#         }
#         await state.update_data(**data)
#         await state.set_state(Registration.full_name)
#         await message.answer(FULLNAME, reply_markup=KB_SITE)


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
    await state.set_state(Registration.plate)
    await message.answer(PLATE)


@rtr.message(Registration.plate)
async def get_plate(message: Message, state: FSMContext):
    await state.update_data(plate=message.text)
    data = await state.get_data()
    await state.clear()
    await message.answer(REGISTERED, reply_markup=KB_REGISTERED)
