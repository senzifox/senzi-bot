import asyncio
import logging

import aiohttp
from aiogram import Dispatcher
from dotenv import load_dotenv

from bot.handlers.currency import router as currency_router
from bot.handlers.downloader import router as downloader_router
from bot.queue import create_queue_pool
from bot.telegram_api import create_bot

load_dotenv()


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    )

    bot = create_bot()
    dp = Dispatcher()
    dp.include_router(downloader_router)
    dp.include_router(currency_router)

    queue = await create_queue_pool()

    async with aiohttp.ClientSession() as http_session:
        logging.info("Стартуем polling")
        await dp.start_polling(bot, queue=queue, http_session=http_session)


if __name__ == "__main__":
    asyncio.run(main())
