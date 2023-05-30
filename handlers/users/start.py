from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import dp
from states.personalData import PersonalData


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await message.answer(f"Salom, iltimos ism familiyangizni kiriting!")
    await PersonalData.fullName.set()