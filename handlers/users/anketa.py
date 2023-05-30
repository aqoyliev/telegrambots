from aiogram.types import Message, CallbackQuery, InputFile
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from data.config import CHANNELS, ADMINS
from loader import dp, bot
from states.personalData import PersonalData
from states.newpost import NewPost
from keyboards.inline.manage_post import confirmation_keyboard, post_callback
from utils.misc.generate_pdf import get_pdf


# /form komandasi uchun handler yaratamiz. Bu yerda foydalanuvchi hech qanday holatda emas, state=None
@dp.message_handler(Command("form"), state=None)
async def enter_test(message: Message):
    await message.answer("Iltimos, ism familiyangizni kiriting!")
    await PersonalData.fullName.set()


@dp.message_handler(state=PersonalData.fullName)
async def answer_fullname(message: Message, state: FSMContext):
    fullname = message.text
    await state.update_data(
        {"name": fullname}
    )

    await message.answer("Email manzil kiriting")

    # await PersonalData.email.set()
    await PersonalData.next()

@dp.message_handler(state=PersonalData.email)
async def answer_email(message: Message, state: FSMContext):
    email = message.text

    await state.update_data(
        {"email": email}
    )

    await message.answer("Telefon raqam kiriting")

    await PersonalData.next()


@dp.message_handler(state=PersonalData.phoneNum)
async def answer_phone(message: Message, state: FSMContext):
    phone = message.text
    await state.update_data(
        {"phone": phone,
         "mention": message.from_user.get_mention()}
    )
    # Ma`lumotlarni qayta o'qiymiz
    data = await state.get_data()
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    # msg = f"Foydalanuvchi {message.from_user.get_mention()} botda ro'yxatdan o'tdi:\n"
    msg = f"Ism Familiya:  {name}\n"
    msg += f"Elektron pochta:  {email}\n"
    msg += f"Telefon:  {phone}"
    await message.answer(msg)
    await message.answer("Ma'lumotlaringiz to'g'rimi yoki qayta kiritasizmi?", reply_markup=confirmation_keyboard())
    await NewPost.Confirm.set()

@dp.callback_query_handler(post_callback.filter(action="post"), state=NewPost.Confirm)
async def confirm_post(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        text = data.get("text")
        mention = data.get("mention")
    await call.message.edit_reply_markup()
    await call.answer("Ma'lumotlaringiz saqlandi.", show_alert=True)
    # Ma`lumotlarni qayta o'qiymiz
    data = await state.get_data()
    full_name = str(data.get("name"))
    email = str(data.get("email"))
    phone = str(data.get("phone"))
    get_pdf(full_name, email, phone)
    target_channel = CHANNELS[0]
    await bot.send_document(chat_id=target_channel, document=InputFile('output.pdf'),
                            caption=f"Foydalanuvchi {mention} botda ro'yxatdan o'tdi:\n")
    await state.finish()

@dp.callback_query_handler(post_callback.filter(action="reform"), state=NewPost.Confirm)
async def cancel_post(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_reply_markup()
    await call.message.answer("Iltimos, ism familiyangizni kiriting!")
    await PersonalData.fullName.set()

@dp.message_handler(state=NewPost.Confirm)
async def post_unknown(message: Message):
    await message.answer("Tasdiqlash yoki qayta kiritishni tanlang!")