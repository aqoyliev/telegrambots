import re
import os
import asyncio
import tempfile
from dataclasses import dataclass, field

from aiogram import types
from loader import bot

try:
    from nudenet import NudeDetector
    _detector = NudeDetector()
    NUDENET_AVAILABLE = True
except Exception:
    NUDENET_AVAILABLE = False

# Profile photo labels that indicate explicit content
_NSFW_LABELS = {
    'EXPOSED_BREAST_F',
    'EXPOSED_GENITALIA_F',
    'EXPOSED_GENITALIA_M',
    'EXPOSED_BUTTOCKS',
    'EXPOSED_ANUS',
}

_LINK_RE = re.compile(r't\.me/\S+|https?://\S+|@[a-zA-Z0-9_]{5,}')


@dataclass
class ProfileResult:
    suspicious: bool
    reasons: list = field(default_factory=list)
    is_bot_like: bool = False


async def check_profile(user: types.User, chat_id: int) -> ProfileResult:
    reasons = []
    is_bot_like = user.is_bot

    # Check bio / description for links
    try:
        chat_member = await bot.get_chat(user.id)
        bio = getattr(chat_member, 'bio', '') or ''
        if _LINK_RE.search(bio):
            reasons.append("profile bio looks like spam/ads")
    except Exception:
        pass

    # Check profile photo for explicit content
    if NUDENET_AVAILABLE:
        photo_suspicious = await _check_profile_photo(user.id)
        if photo_suspicious:
            reasons.append("profile photo contains explicit content")

    return ProfileResult(
        suspicious=bool(reasons) or is_bot_like,
        reasons=reasons,
        is_bot_like=is_bot_like,
    )


async def _check_profile_photo(user_id: int) -> bool:
    try:
        photos = await bot.get_user_profile_photos(user_id, limit=1)
        if not photos.photos:
            return False

        file_id = photos.photos[0][-1].file_id
        file_info = await bot.get_file(file_id)

        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            tmp_path = tmp.name

        await bot.download_file(file_info.file_path, destination=tmp_path)

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, _detector.detect, tmp_path)
        os.unlink(tmp_path)

        return any(
            d.get('class') in _NSFW_LABELS and d.get('score', 0) > 0.6
            for d in result
        )
    except Exception:
        return False
