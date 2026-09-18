from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bot.services.crypto import CryptoError, get_usd_prices


def _mock_session(status: int, json_body: dict):
    mock_response = AsyncMock()
    mock_response.status = status
    mock_response.json = AsyncMock(return_value=json_body)

    mock_get_cm = AsyncMock()
    mock_get_cm.__aenter__.return_value = mock_response

    mock_session = MagicMock()
    mock_session.get.return_value = mock_get_cm

    mock_session_cm = AsyncMock()
    mock_session_cm.__aenter__.return_value = mock_session
    return mock_session_cm


@patch("bot.services.crypto.aiohttp.ClientSession")
async def test_get_usd_prices_success(mock_session_cls):
    mock_session_cls.return_value = _mock_session(200, {"bitcoin": {"usd": 60000.0}})

    prices = await get_usd_prices(["bitcoin"])

    assert prices == {"bitcoin": 60000.0}


@patch("bot.services.crypto.aiohttp.ClientSession")
async def test_get_usd_prices_http_error(mock_session_cls):
    mock_session_cls.return_value = _mock_session(500, {})

    with pytest.raises(CryptoError, match="HTTP 500"):
        await get_usd_prices(["bitcoin"])


@patch("bot.services.crypto.aiohttp.ClientSession")
async def test_get_usd_prices_unknown_coin(mock_session_cls):
    mock_session_cls.return_value = _mock_session(200, {})

    with pytest.raises(CryptoError, match="not-a-coin"):
        await get_usd_prices(["not-a-coin"])
