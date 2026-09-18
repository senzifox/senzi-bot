import pytest

from bot.handlers.currency import parse_currency_query


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("usd rub 100", (100.0, "USD", "RUB")),
        ("100 usd rub", (100.0, "USD", "RUB")),
        ("usd 100 rub", (100.0, "USD", "RUB")),
        ("USD RUB 100", (100.0, "USD", "RUB")),
        ("usd rub", (1.0, "USD", "RUB")),
        ("100.5 usd rub", (100.5, "USD", "RUB")),
        ("100,5 usd rub", (100.5, "USD", "RUB")),
        ("100 usd to rub", (100.0, "USD", "RUB")),
        ("btc usd 1", (1.0, "BTC", "USD")),
        ("1 btc eth", (1.0, "BTC", "ETH")),
        ("btc rub", (1.0, "BTC", "RUB")),
    ],
)
def test_parse_currency_query_matches(text, expected):
    assert parse_currency_query(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "just a regular message",
        "100 usd",
        "usd eur gbp",
        "usd usd 100",
        "100 200 usd rub",
    ],
)
def test_parse_currency_query_does_not_match(text):
    assert parse_currency_query(text) is None
