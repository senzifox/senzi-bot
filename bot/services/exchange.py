import aiohttp

from bot.services.crypto import TICKER_TO_COINGECKO_ID, CryptoError, get_usd_prices
from bot.services.currency import CurrencyError, convert_currency

COINGECKO_ID_TO_TICKER = {v: k for k, v in TICKER_TO_COINGECKO_ID.items()}


class ExchangeError(Exception):
    pass


def _wrap_crypto_error(e: CryptoError) -> ExchangeError:
    if e.coingecko_id is not None:
        ticker = COINGECKO_ID_TO_TICKER.get(e.coingecko_id, e.coingecko_id)
        return ExchangeError(f"не знаю валюту {ticker}")
    return ExchangeError(str(e))


async def convert(
    session: aiohttp.ClientSession, amount: float, from_code: str, to_code: str
) -> float:
    from_id = TICKER_TO_COINGECKO_ID.get(from_code)
    to_id = TICKER_TO_COINGECKO_ID.get(to_code)

    try:
        if from_id is None and to_id is None:
            return await convert_currency(session, amount, from_code, to_code)

        if from_id is not None and to_id is not None:
            prices = await get_usd_prices(session, [from_id, to_id])
            amount_usd = amount * prices[from_id]
            return amount_usd / prices[to_id]

        if from_id is not None:
            prices = await get_usd_prices(session, [from_id])
            amount_usd = amount * prices[from_id]
            if to_code == "USD":
                return amount_usd
            return await convert_currency(session, amount_usd, "USD", to_code)

        prices = await get_usd_prices(session, [to_id])
        amount_usd = (
            amount
            if from_code == "USD"
            else await convert_currency(session, amount, from_code, "USD")
        )
        return amount_usd / prices[to_id]
    except CryptoError as e:
        raise _wrap_crypto_error(e) from e
    except CurrencyError as e:
        raise ExchangeError(str(e)) from e
