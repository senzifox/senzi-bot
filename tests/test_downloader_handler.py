import pytest

from bot.handlers.downloader import find_youtube_url


@pytest.mark.parametrize(
    ("text", "expected_url"),
    [
        (
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        ),
        ("youtube.com/watch?v=dQw4w9WgXcQ", "https://youtube.com/watch?v=dQw4w9WgXcQ"),
        ("https://youtu.be/dQw4w9WgXcQ", "https://youtu.be/dQw4w9WgXcQ"),
        ("youtu.be/dQw4w9WgXcQ", "https://youtu.be/dQw4w9WgXcQ"),
        (
            "check this out youtu.be/dQw4w9WgXcQ nice",
            "https://youtu.be/dQw4w9WgXcQ",
        ),
        (
            "www.youtube.com/shorts/dQw4w9WgXcQ",
            "https://www.youtube.com/shorts/dQw4w9WgXcQ",
        ),
        ("youtube.com/live/dQw4w9WgXcQ", "https://youtube.com/live/dQw4w9WgXcQ"),
        (
            "m.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
        ),
        (
            "YOUTUBE.COM/watch?v=dQw4w9WgXcQ",
            "https://YOUTUBE.COM/watch?v=dQw4w9WgXcQ",
        ),
    ],
)
def test_find_youtube_url_matches(text, expected_url):
    assert find_youtube_url(text) == expected_url


@pytest.mark.parametrize(
    "text",
    [
        "just a regular message",
        "https://vimeo.com/12345",
        "youtube.com/results?search_query=cats",
    ],
)
def test_find_youtube_url_does_not_match(text):
    assert find_youtube_url(text) is None
