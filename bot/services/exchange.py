from bot.services.crypto import TICKER_TO_COINGECKO_ID, CryptoError, get_usd_prices
from bot.services.currency import CurrencyError, convert_currency


class ExchangeError(Exception):
    pass


async def convert(amount: float, from_code: str, to_code: str) -> float:
    from_id = TICKER_TO_COINGECKO_ID.get(from_code)
    to_id = TICKER_TO_COINGECKO_ID.get(to_code)

    try:
        if from_id is None and to_id is None:
            return await convert_currency(amount, from_code, to_code)

        if from_id is not None and to_id is not None:
            prices = await get_usd_prices([from_id, to_id])
            amount_usd = amount * prices[from_id]
            return amount_usd / prices[to_id]

        if from_id is not None:
            prices = await get_usd_prices([from_id])
            amount_usd = amount * prices[from_id]
            if to_code == "USD":
                return amount_usd
            return await convert_currency(amount_usd, "USD", to_code)

        prices = await get_usd_prices([to_id])
        amount_usd = (
            amount if from_code == "USD" else await convert_currency(amount, from_code, "USD")
        )
        return amount_usd / prices[to_id]
    except (CryptoError, CurrencyError) as e:
        raise ExchangeError(str(e)) from e
