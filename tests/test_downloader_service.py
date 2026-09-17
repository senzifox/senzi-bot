from unittest.mock import MagicMock, patch

import pytest
from yt_dlp.utils import DownloadError as YtDlpDownloadError

from bot.services.downloader import DownloadError, download_video


@patch("bot.services.downloader.yt_dlp.YoutubeDL")
def test_download_video_returns_prepared_file_path(mock_youtube_dl, tmp_path):
    downloaded_file = tmp_path / "abc123.mp4"
    downloaded_file.write_bytes(b"fake video bytes")

    info = {"title": "Test video", "filesize": 1000}

    mock_ydl = MagicMock()
    mock_ydl.extract_info.return_value = info
    mock_ydl.process_ie_result.return_value = {"id": "abc123", "ext": "mp4"}
    mock_ydl.prepare_filename.return_value = str(downloaded_file)
    mock_youtube_dl.return_value.__enter__.return_value = mock_ydl

    result = download_video("https://youtu.be/abc123", tmp_path)

    assert result == downloaded_file
    mock_ydl.extract_info.assert_called_once_with("https://youtu.be/abc123", download=False)
    mock_ydl.process_ie_result.assert_called_once_with(info, download=True)


@patch("bot.services.downloader.yt_dlp.YoutubeDL")
def test_download_video_wraps_yt_dlp_error(mock_youtube_dl, tmp_path):
    mock_ydl = MagicMock()
    mock_ydl.extract_info.side_effect = YtDlpDownloadError("video unavailable")
    mock_youtube_dl.return_value.__enter__.return_value = mock_ydl

    with pytest.raises(DownloadError, match="video unavailable"):
        download_video("https://youtu.be/dead", tmp_path)


@patch("bot.services.downloader.yt_dlp.YoutubeDL")
def test_download_video_rejects_live_stream(mock_youtube_dl, tmp_path):
    mock_ydl = MagicMock()
    mock_ydl.extract_info.return_value = {"title": "Live now", "is_live": True}
    mock_youtube_dl.return_value.__enter__.return_value = mock_ydl

    with pytest.raises(DownloadError, match="прямой эфир"):
        download_video("https://youtu.be/live", tmp_path)

    mock_ydl.process_ie_result.assert_not_called()


@patch("bot.services.downloader.yt_dlp.YoutubeDL")
def test_download_video_rejects_upcoming_stream(mock_youtube_dl, tmp_path):
    mock_ydl = MagicMock()
    mock_ydl.extract_info.return_value = {
        "title": "Premieres soon",
        "is_live": False,
        "live_status": "is_upcoming",
    }
    mock_youtube_dl.return_value.__enter__.return_value = mock_ydl

    with pytest.raises(DownloadError, match="прямой эфир"):
        download_video("https://youtu.be/upcoming", tmp_path)


@patch("bot.services.downloader.yt_dlp.YoutubeDL")
def test_download_video_rejects_upfront_when_estimated_size_too_large(mock_youtube_dl, tmp_path):
    mock_ydl = MagicMock()
    mock_ydl.extract_info.return_value = {
        "title": "Huge video",
        "requested_formats": [
            {"filesize": 200 * 1024 * 1024},
            {"filesize": 40 * 1024 * 1024},
        ],
    }
    mock_youtube_dl.return_value.__enter__.return_value = mock_ydl

    with pytest.raises(DownloadError, match="примерно"):
        download_video("https://youtu.be/huge", tmp_path)

    mock_ydl.extract_info.assert_called_once_with("https://youtu.be/huge", download=False)


@patch("bot.services.downloader.TELEGRAM_BOT_API_FILE_LIMIT_BYTES", 10)
@patch("bot.services.downloader.yt_dlp.YoutubeDL")
def test_download_video_rejects_after_download_when_estimate_unavailable(mock_youtube_dl, tmp_path):
    downloaded_file = tmp_path / "abc123.mp4"
    downloaded_file.write_bytes(b"this is way more than ten bytes")

    mock_ydl = MagicMock()
    mock_ydl.extract_info.return_value = {"title": "Unknown size video"}
    mock_ydl.process_ie_result.return_value = {"id": "abc123", "ext": "mp4"}
    mock_ydl.prepare_filename.return_value = str(downloaded_file)
    mock_youtube_dl.return_value.__enter__.return_value = mock_ydl

    with pytest.raises(DownloadError) as exc_info:
        download_video("https://youtu.be/abc123", tmp_path)

    assert "примерно" not in str(exc_info.value)
    mock_ydl.process_ie_result.assert_called_once()
