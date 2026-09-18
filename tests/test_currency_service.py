import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from bot.services import currency as currency_module
from bot.services.currency import CurrencyError, convert_currency


def _mock_session(status: int, json_body: dict):
    mock_response = AsyncMock()
    mock_response.status = status
    mock_response.json = AsyncMock(return_value=json_body)

    mock_get_cm = AsyncMock()
    mock_get_cm.__aenter__.return_value = mock_response

    mock_session = MagicMock()
    mock_session.get.return_value = mock_get_cm
    return mock_session


@pytest.fixture(autouse=True)
def _clear_cache():
    currency_module._rates_cache.clear()
    currency_module._fetch_locks.clear()
    yield
    currency_module._rates_cache.clear()
    currency_module._fetch_locks.clear()


async def test_convert_currency_success():
    session = _mock_session(200, {"result": "success", "rates": {"RUB": 90.0}})

    result = await convert_currency(session, 10, "USD", "RUB")

    assert result == 900.0


async def test_convert_currency_unknown_target():
    session = _mock_session(200, {"result": "success", "rates": {"RUB": 90.0}})

    with pytest.raises(CurrencyError, match="XXX"):
        await convert_currency(session, 10, "USD", "XXX")


async def test_convert_currency_http_error():
    session = _mock_session(500, {})

    with pytest.raises(CurrencyError, match="HTTP 500"):
        await convert_currency(session, 10, "USD", "RUB")


async def test_convert_currency_uses_cache_on_second_call():
    session = _mock_session(200, {"result": "success", "rates": {"RUB": 90.0}})

    await convert_currency(session, 10, "USD", "RUB")
    await convert_currency(session, 5, "USD", "RUB")

    assert session.get.call_count == 1


async def test_concurrent_calls_for_same_base_fetch_once():
    session = _mock_session(200, {"result": "success", "rates": {"RUB": 90.0}})

    await asyncio.gather(*[convert_currency(session, 1, "USD", "RUB") for _ in range(5)])

    assert session.get.call_count == 1
