from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

post_callback = CallbackData("create_post", "action")

def confirmation_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="🆗 Ha", callback_data=post_callback.new(action="post")),
            InlineKeyboardButton(text="🔁 Qayta kiritish", callback_data=post_callback.new(action="reform")),
        ]]
    )
    return keyboard