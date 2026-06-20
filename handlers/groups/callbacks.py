from aiogram import types
from aiogram.dispatcher.filters import ChatTypeFilter

from loader import dp, bot
from utils.moderation import unmute_user, ban_user


async def _caller_is_admin(admin_id: int) -> bool:
    from data import config
    return str(admin_id) in [str(a) for a in config.ADMINS]


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("mod:"))
async def handle_mod_action(call: types.CallbackQuery):
    if not await _caller_is_admin(call.from_user.id):
        await call.answer("You are not authorized.", show_alert=True)
        return

    _, action, chat_id, user_id = call.data.split(":")
    chat_id, user_id = int(chat_id), int(user_id)

    if action == "unmute":
        try:
            await unmute_user(chat_id, user_id)
            await call.answer("✅ User unmuted.")
            await call.message.edit_text(
                call.message.text + "\n\n✅ <b>Unmuted</b> by " + call.from_user.full_name
            )
        except Exception as e:
            await call.answer(f"Error: {e}", show_alert=True)

    elif action == "ban":
        try:
            await ban_user(chat_id, user_id)
            await call.answer("🚫 User banned.")
            await call.message.edit_text(
                call.message.text + "\n\n🚫 <b>Banned</b> by " + call.from_user.full_name
            )
        except Exception as e:
            await call.answer(f"Error: {e}", show_alert=True)
