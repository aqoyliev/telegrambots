from datetime import datetime, timedelta

from aiogram import types
from aiogram.types import ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton

from loader import bot
from data import config
from utils.profile_checker import ProfileResult
from utils.ai_checker import SpamResult

_MUTED_PERMISSIONS = ChatPermissions(
    can_send_messages=False,
    can_send_media_messages=False,
    can_send_other_messages=False,
    can_add_web_page_previews=False,
)


async def mute_user(chat_id: int, user_id: int, hours: int = 24):
    until = datetime.now() + timedelta(hours=hours)
    await bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        permissions=_MUTED_PERMISSIONS,
        until_date=until,
    )


async def unmute_user(chat_id: int, user_id: int):
    await bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        permissions=ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
        ),
    )


async def ban_user(chat_id: int, user_id: int):
    await bot.kick_chat_member(chat_id=chat_id, user_id=user_id)


def _action_kb(chat_id: int, user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("✅ Unmute", callback_data=f"mod:unmute:{chat_id}:{user_id}"),
        InlineKeyboardButton("🚫 Ban", callback_data=f"mod:ban:{chat_id}:{user_id}"),
    )
    return kb


def _user_link(user: types.User) -> str:
    name = user.full_name
    if user.username:
        return f'<a href="tg://user?id={user.id}">{name}</a> (@{user.username})'
    return f'<a href="tg://user?id={user.id}">{name}</a>'


async def notify_admins_join(user: types.User, chat: types.Chat, result: ProfileResult):
    reasons_text = "\n".join(f"• {r}" for r in result.reasons) if result.reasons else "• bot account detected"
    text = (
        f"🚨 <b>Suspicious profile on join</b>\n"
        f"{_user_link(user)}\n"
        f"<code>{user.id}</code>\n"
        f"📌 {chat.title}\n\n"
        f"{reasons_text}\n\n"
        f"⚠️ Muted 24h pending review — unmute if this is a false positive."
    )
    kb = _action_kb(chat.id, user.id)
    for admin_id in config.ADMINS:
        try:
            await bot.send_message(admin_id, text, reply_markup=kb)
        except Exception:
            pass


async def notify_admins_spam(
    message: types.Message,
    spam_result: SpamResult,
    profile_result: ProfileResult,
):
    user = message.from_user
    reasons = []
    if spam_result.reason:
        reasons.append(f"spam: {spam_result.reason}")
    reasons.extend(profile_result.reasons)
    reasons_text = "\n".join(f"• {r}" for r in reasons) or "• spam detected"

    preview = (message.text or message.caption or "")[:200]
    text = (
        f"🛑 <b>Spam message deleted</b>\n"
        f"{_user_link(user)}\n"
        f"<code>{user.id}</code>\n"
        f"📌 {message.chat.title}\n\n"
        f"{reasons_text}\n\n"
        f"💬 <i>{preview}</i>\n\n"
        f"⚠️ User muted 24h."
    )
    kb = _action_kb(message.chat.id, user.id)
    for admin_id in config.ADMINS:
        try:
            await bot.send_message(admin_id, text, reply_markup=kb)
        except Exception:
            pass
