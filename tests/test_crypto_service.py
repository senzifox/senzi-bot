from unittest.mock import AsyncMock, MagicMock

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
    return mock_session


async def test_get_usd_prices_success():
    session = _mock_session(200, {"bitcoin": {"usd": 60000.0}})

    prices = await get_usd_prices(session, ["bitcoin"])

    assert prices == {"bitcoin": 60000.0}


async def test_get_usd_prices_http_error():
    session = _mock_session(500, {})

    with pytest.raises(CryptoError, match="HTTP 500"):
        await get_usd_prices(session, ["bitcoin"])


async def test_get_usd_prices_unknown_coin():
    session = _mock_session(200, {})

    with pytest.raises(CryptoError, match="not-a-coin") as exc_info:
        await get_usd_prices(session, ["not-a-coin"])

    assert exc_info.value.coingecko_id == "not-a-coin"
