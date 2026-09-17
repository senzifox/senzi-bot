import asyncio
import logging
from pathlib import Path
from uuid import uuid4

from aiogram import Router
from aiogram.types import FSInputFile, Message
from yt_dlp.extractor.youtube import YoutubeIE

from bot.services.downloader import DownloadError, download_video

router = Router(name="downloader")
logger = logging.getLogger(__name__)

DOWNLOADS_DIR = Path("downloads")


def find_youtube_url(text: str) -> str | None:
    for token in text.split():
        candidate = token if "://" in token else f"https://{token}"
        if YoutubeIE.suitable(candidate.lower()):
            return candidate
    return None


def youtube_link(message: Message) -> dict[str, str] | bool:
    if not message.text:
        return False
    url = find_youtube_url(message.text)
    return {"youtube_url": url} if url else False


@router.message(youtube_link)
async def handle_youtube_link(message: Message, youtube_url: str) -> None:
    logger.info("Ссылка от %s: %s", message.from_user.id if message.from_user else "?", youtube_url)
    status = await message.answer("Скачивание...")
    job_dir = DOWNLOADS_DIR / uuid4().hex

    try:
        job_dir.mkdir(parents=True)
        file_path = await asyncio.to_thread(download_video, youtube_url, job_dir)
        await message.answer_video(FSInputFile(file_path))
        logger.info("Отправлено %s", file_path.name)
    except DownloadError as e:
        logger.warning("Отказ по %s: %s", youtube_url, e)
        await message.answer(f"Не удалось скачать: {e}")
    except Exception:
        logger.exception("Ошибка при скачивании %s", youtube_url)
        await message.answer("Что-то сломалось на моей стороне, гляну логи")
    finally:
        await status.delete()
        if job_dir.exists():
            for f in job_dir.iterdir():
                f.unlink(missing_ok=True)
            job_dir.rmdir()
