import asyncio
import os
from pathlib import Path

from aiogram import Bot
from aiogram.types import FSInputFile
from dotenv import load_dotenv

from bot.access import get_primary_admin_id

load_dotenv()

PLACEHOLDER_PATH = Path(__file__).parent.parent / "bot" / "assets" / "placeholder.png"


async def main() -> None:
    bot = Bot(token=os.environ["BOT_TOKEN"])
    message = await bot.send_photo(
        chat_id=get_primary_admin_id(),
        photo=FSInputFile(PLACEHOLDER_PATH),
    )
    file_id = message.photo[-1].file_id
    await bot.session.close()

    print(f"PLACEHOLDER_PHOTO_FILE_ID={file_id}")
    print("Добавь эту строку в .env. Сообщение в чате можно удалить вручную.")


if __name__ == "__main__":
    asyncio.run(main())
