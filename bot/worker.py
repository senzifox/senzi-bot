import asyncio
import logging
import os
from pathlib import Path
from uuid import uuid4

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile, InputMediaVideo
from dotenv import load_dotenv

from bot.queue import get_redis_settings
from bot.services.downloader import DownloadError, download_video

load_dotenv()

logger = logging.getLogger(__name__)

DOWNLOADS_DIR = Path("downloads")


async def download_youtube_job(
    ctx: dict, url: str, inline_message_id: str, requester_user_id: int
) -> None:
    bot: Bot = ctx["bot"]
    job_dir = DOWNLOADS_DIR / uuid4().hex
    job_dir.mkdir(parents=True, exist_ok=True)
    uploaded = None

    try:
        file_path = await asyncio.to_thread(download_video, url, job_dir)
        uploaded = await bot.send_video(
            chat_id=requester_user_id,
            video=FSInputFile(file_path),
            disable_notification=True,
        )
        await bot.edit_message_media(
            inline_message_id=inline_message_id,
            media=InputMediaVideo(media=uploaded.video.file_id),
        )
    except DownloadError as e:
        await bot.edit_message_caption(
            inline_message_id=inline_message_id,
            caption=f"Не удалось скачать: {e}",
        )
    except Exception:
        logger.exception("Ошибка при скачивании %s", url)
        await bot.edit_message_caption(
            inline_message_id=inline_message_id,
            caption="Что-то сломалось на моей стороне, гляну логи",
        )
    finally:
        if uploaded is not None:
            await uploaded.delete()
        for f in job_dir.iterdir():
            f.unlink(missing_ok=True)
        job_dir.rmdir()


async def startup(ctx: dict) -> None:
    ctx["bot"] = Bot(
        token=os.environ["BOT_TOKEN"],
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


async def shutdown(ctx: dict) -> None:
    await ctx["bot"].session.close()


class WorkerSettings:
    functions = [download_youtube_job]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = get_redis_settings()
