import asyncio
import logging
import os
from pathlib import Path
from uuid import uuid4

from aiogram import Router
from aiogram.types import (
    ChosenInlineResult,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultCachedPhoto,
    Message,
)
from arq import ArqRedis
from yt_dlp.extractor.youtube import YoutubeIE

from bot.access import AccessControlMiddleware
from bot.services.downloader import DownloadError, download_video

router = Router(name="downloader")
router.message.middleware(AccessControlMiddleware())
router.inline_query.middleware(AccessControlMiddleware())

logger = logging.getLogger(__name__)

DOWNLOADS_DIR = Path("downloads")

pending_inline_urls: dict[str, str] = {}


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
        await message.answer("Что-то сломалось на моей стороне")
    finally:
        await status.delete()
        if job_dir.exists():
            for f in job_dir.iterdir():
                f.unlink(missing_ok=True)
            job_dir.rmdir()


def youtube_inline_query(inline_query: InlineQuery) -> dict[str, str] | bool:
    url = find_youtube_url(inline_query.query)
    return {"youtube_url": url} if url else False


@router.inline_query(youtube_inline_query)
async def handle_youtube_inline_query(inline_query: InlineQuery, youtube_url: str) -> None:
    logger.info("Inline-запрос от %s: %s", inline_query.from_user.id, youtube_url)
    result_id = uuid4().hex
    pending_inline_urls[result_id] = youtube_url
    await inline_query.answer(
        [
            InlineQueryResultCachedPhoto(
                id=result_id,
                photo_file_id=os.environ["PLACEHOLDER_PHOTO_FILE_ID"],
                caption="Скачивание...",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="Открыть на YouTube", url=youtube_url)]
                    ]
                ),
            )
        ],
        cache_time=1,
        is_personal=True,
    )


@router.chosen_inline_result()
async def handle_chosen_youtube_result(chosen: ChosenInlineResult, queue: ArqRedis) -> None:
    youtube_url = pending_inline_urls.pop(chosen.result_id, None)
    logger.info(
        "chosen_inline_result от %s: result_id=%s url=%s inline_message_id=%s",
        chosen.from_user.id,
        chosen.result_id,
        youtube_url,
        chosen.inline_message_id,
    )
    if youtube_url is None or chosen.inline_message_id is None:
        logger.warning("Пропускаю enqueue: url или inline_message_id отсутствует")
        return
    await queue.enqueue_job(
        "download_youtube_job", youtube_url, chosen.inline_message_id, chosen.from_user.id
    )
    logger.info("Задача поставлена в очередь: %s", youtube_url)
