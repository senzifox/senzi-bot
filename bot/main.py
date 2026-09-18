import asyncio
import logging
import os

import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

from bot.handlers.currency import router as currency_router
from bot.handlers.downloader import router as downloader_router
from bot.queue import create_queue_pool

load_dotenv()


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    )

    bot = Bot(
        token=os.environ["BOT_TOKEN"],
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(downloader_router)
    dp.include_router(currency_router)

    queue = await create_queue_pool()

    async with aiohttp.ClientSession() as http_session:
        logging.info("Стартуем polling")
        await dp.start_polling(bot, queue=queue, http_session=http_session)


if __name__ == "__main__":
    asyncio.run(main())
