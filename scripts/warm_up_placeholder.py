import asyncio
import os
from pathlib import Path

from aiogram import Bot
from aiogram.types import FSInputFile
from dotenv import load_dotenv

from bot.access import get_primary_admin_id

load_dotenv()

ASSETS_DIR = Path(__file__).parent.parent / "bot" / "assets"

ICONS = {
    "PLACEHOLDER_PHOTO_FILE_ID": ASSETS_DIR / "placeholder.png",
    "CURRENCY_PLACEHOLDER_PHOTO_FILE_ID": ASSETS_DIR / "currency_placeholder.png",
}


async def main() -> None:
    bot = Bot(token=os.environ["BOT_TOKEN"])
    admin_id = get_primary_admin_id()

    lines = []
    for env_name, path in ICONS.items():
        message = await bot.send_photo(chat_id=admin_id, photo=FSInputFile(path))
        lines.append(f"{env_name}={message.photo[-1].file_id}")

    await bot.session.close()

    print("\n".join(lines))
    print("Добавь эти строки в .env. Сообщения в чате можно удалить вручную.")


if __name__ == "__main__":
    asyncio.run(main())
