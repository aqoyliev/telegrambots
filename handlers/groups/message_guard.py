from aiogram import types
from aiogram.dispatcher.filters import ChatTypeFilter

from loader import dp, bot
from utils.ai_checker import check_message_spam
from utils.profile_checker import check_profile
from utils.moderation import mute_user, notify_admins_spam


async def _is_admin(chat_id: int, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.is_chat_admin()
    except Exception:
        return False


@dp.message_handler(
    ChatTypeFilter(types.ChatType.SUPERGROUP),
    content_types=types.ContentType.ANY,
)
async def guard_message(message: types.Message):
    if not message.from_user or message.from_user.is_bot:
        return

    if await _is_admin(message.chat.id, message.from_user.id):
        return

    text = message.text or message.caption or ""
    spam_result = await check_message_spam(text)

    if spam_result.is_spam:
        try:
            await message.delete()
        except Exception:
            pass

        await mute_user(message.chat.id, message.from_user.id, hours=24)
        profile_result = await check_profile(message.from_user, message.chat.id)

        if profile_result.is_bot_like:
            from utils.moderation import ban_user
            await ban_user(message.chat.id, message.from_user.id)
            return

        await notify_admins_spam(message, spam_result, profile_result)
