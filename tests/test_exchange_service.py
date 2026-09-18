from unittest.mock import AsyncMock, patch

import pytest

from bot.services.crypto import CryptoError
from bot.services.currency import CurrencyError
from bot.services.exchange import ExchangeError, convert


@patch("bot.services.exchange.convert_currency", new_callable=AsyncMock)
async def test_convert_fiat_to_fiat(mock_convert_currency):
    mock_convert_currency.return_value = 9000.0

    result = await convert(100, "USD", "RUB")

    assert result == 9000.0
    mock_convert_currency.assert_awaited_once_with(100, "USD", "RUB")


@patch("bot.services.exchange.get_usd_prices", new_callable=AsyncMock)
async def test_convert_crypto_to_usd(mock_get_usd_prices):
    mock_get_usd_prices.return_value = {"bitcoin": 60000.0}

    result = await convert(2, "BTC", "USD")

    assert result == 120000.0


@patch("bot.services.exchange.convert_currency", new_callable=AsyncMock)
@patch("bot.services.exchange.get_usd_prices", new_callable=AsyncMock)
async def test_convert_crypto_to_fiat(mock_get_usd_prices, mock_convert_currency):
    mock_get_usd_prices.return_value = {"bitcoin": 60000.0}
    mock_convert_currency.return_value = 5400000.0

    result = await convert(1, "BTC", "RUB")

    mock_convert_currency.assert_awaited_once_with(60000.0, "USD", "RUB")
    assert result == 5400000.0


@patch("bot.services.exchange.convert_currency", new_callable=AsyncMock)
@patch("bot.services.exchange.get_usd_prices", new_callable=AsyncMock)
async def test_convert_fiat_to_crypto(mock_get_usd_prices, mock_convert_currency):
    mock_convert_currency.return_value = 100.0
    mock_get_usd_prices.return_value = {"bitcoin": 50.0}

    result = await convert(9000, "RUB", "BTC")

    mock_convert_currency.assert_awaited_once_with(9000, "RUB", "USD")
    assert result == 2.0


@patch("bot.services.exchange.get_usd_prices", new_callable=AsyncMock)
async def test_convert_crypto_to_crypto(mock_get_usd_prices):
    mock_get_usd_prices.return_value = {"bitcoin": 60000.0, "ethereum": 3000.0}

    result = await convert(1, "BTC", "ETH")

    assert result == 20.0


@patch("bot.services.exchange.convert_currency", new_callable=AsyncMock)
async def test_convert_wraps_currency_error(mock_convert_currency):
    mock_convert_currency.side_effect = CurrencyError("не знаю валюту XXX")

    with pytest.raises(ExchangeError, match="не знаю валюту"):
        await convert(1, "USD", "XXX")


@patch("bot.services.exchange.get_usd_prices", new_callable=AsyncMock)
async def test_convert_wraps_crypto_error(mock_get_usd_prices):
    mock_get_usd_prices.side_effect = CryptoError("не знаю курс bitcoin")

    with pytest.raises(ExchangeError, match="не знаю курс"):
        await convert(1, "BTC", "USD")
