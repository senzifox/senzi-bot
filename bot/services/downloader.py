import logging
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yt_dlp
from yt_dlp.utils import DownloadError as YtDlpDownloadError

logger = logging.getLogger(__name__)


class DownloadError(Exception):
    pass


TELEGRAM_BOT_API_FILE_LIMIT_BYTES = 2000 * 1024 * 1024


def _estimate_size_bytes(info: Mapping[str, Any]) -> int | None:
    formats = info.get("requested_formats") or [info]
    sizes: list[int] = []
    for f in formats:
        size = f.get("filesize")
        if size is None:
            size = f.get("filesize_approx")
        if size is None:
            return None
        sizes.append(size)
    return sum(sizes)


def _reject_if_too_large(size_bytes: int, *, estimated: bool) -> None:
    if size_bytes <= TELEGRAM_BOT_API_FILE_LIMIT_BYTES:
        return
    qualifier = "примерно " if estimated else ""
    raise DownloadError(
        f"видео весит {qualifier}{size_bytes / 1024 / 1024:.0f} МБ, "
        f"бот принимает файлы не больше {TELEGRAM_BOT_API_FILE_LIMIT_BYTES // 1024 // 1024} МБ"
    )


def download_video(url: str, out_dir: Path) -> Path:
    opts = {
        "format": "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
        "outtmpl": str(out_dir / "%(id)s.%(ext)s"),
        "merge_output_format": "mp4",
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "noplaylist": True,
    }

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:  # type: ignore[arg-type]
            info = ydl.extract_info(url, download=False)
            if info.get("is_live") or info.get("live_status") == "is_upcoming":
                raise DownloadError("это прямой эфир, живые трансляции пока не поддерживаются")

            estimated_size = _estimate_size_bytes(info)
            logger.info(
                "%s: %s, оценка размера %s",
                url,
                info.get("title"),
                f"~{estimated_size / 1024 / 1024:.0f} МБ" if estimated_size else "неизвестна",
            )
            if estimated_size is not None:
                _reject_if_too_large(estimated_size, estimated=True)

            started_at = time.monotonic()
            info = ydl.process_ie_result(info, download=True)
            file_path = Path(ydl.prepare_filename(info))
            download_seconds = time.monotonic() - started_at
    except YtDlpDownloadError as e:
        raise DownloadError(str(e)) from e

    file_size = file_path.stat().st_size
    logger.info(
        "%s: скачано за %.1fс, %.1f МБ",
        file_path.name,
        download_seconds,
        file_size / 1024 / 1024,
    )
    _reject_if_too_large(file_size, estimated=False)

    return file_path
