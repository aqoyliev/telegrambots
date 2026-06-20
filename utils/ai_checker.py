import json
import asyncio
from dataclasses import dataclass

import google.generativeai as genai
from data import config

genai.configure(api_key=config.GEMINI_API_KEY)
_model = genai.GenerativeModel('gemini-2.5-flash')

_PROMPT = """You are a Telegram group spam moderator.
Analyze the following message and decide if it is spam or advertising.

Spam/advertising signs: selling products, crypto/NFT promotions, channel/group invites,
suspicious links, adult content solicitation, mass recruitment, lottery/giveaway fraud.

Reply ONLY with valid JSON (no markdown):
{{"is_spam": true/false, "reason": "short explanation in Russian"}}

Message:
{text}"""


@dataclass
class SpamResult:
    is_spam: bool
    reason: str


async def check_message_spam(text: str) -> SpamResult:
    if not text or len(text.strip()) < 3:
        return SpamResult(is_spam=False, reason="")

    prompt = _PROMPT.format(text=text[:2000])
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: _model.generate_content(prompt)
        )
        raw = response.text.strip()
        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw)
        return SpamResult(
            is_spam=bool(data.get("is_spam")),
            reason=data.get("reason", ""),
        )
    except Exception:
        return SpamResult(is_spam=False, reason="")
