import os
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import InlineQuery, TelegramObject


def is_allowed(user_id: int) -> bool:
    raw = os.environ.get("ALLOWED_USER_IDS", "")
    allowed_ids = {int(x) for x in raw.split(",") if x.strip()}
    return user_id in allowed_ids


def get_primary_admin_id() -> int:
    raw = os.environ.get("ALLOWED_USER_IDS", "")
    ids = [int(x) for x in raw.split(",") if x.strip()]
    if not ids:
        raise RuntimeError("ALLOWED_USER_IDS пуст — некуда отправить плейсхолдер")
    return ids[0]


class AccessControlMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is None or not is_allowed(user.id):
            if isinstance(event, InlineQuery):
                await event.answer([], cache_time=1)
            return None
        return await handler(event, data)
