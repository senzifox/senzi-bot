import os

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums import ParseMode


def create_bot() -> Bot:
    base_url = os.environ.get("TELEGRAM_API_BASE_URL", "http://telegram-bot-api:8081")
    return Bot(
        token=os.environ["BOT_TOKEN"],
        session=AiohttpSession(api=TelegramAPIServer.from_base(base_url)),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
