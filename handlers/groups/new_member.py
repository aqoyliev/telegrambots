from aiogram import types

from loader import dp
from utils.profile_checker import check_profile
from utils.moderation import mute_user, ban_user, notify_admins_join


@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def on_new_member(message: types.Message):
    for user in message.new_chat_members:
        if user.is_bot:
            await ban_user(message.chat.id, user.id)
            try:
                await message.delete()
            except Exception:
                pass
            return

        result = await check_profile(user, message.chat.id)
        if result.is_bot_like:
            await ban_user(message.chat.id, user.id)
            try:
                await message.delete()
            except Exception:
                pass
            return

        if result.suspicious:
            await mute_user(message.chat.id, user.id, hours=24)
            await notify_admins_join(user, message.chat, result)
