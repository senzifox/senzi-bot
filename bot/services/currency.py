import time

import aiohttp

RATES_API_URL = "https://open.er-api.com/v6/latest/{base}"
CACHE_TTL_SECONDS = 3600

_rates_cache: dict[str, tuple[dict[str, float], float]] = {}


class CurrencyError(Exception):
    pass


async def _fetch_rates(base_code: str) -> dict[str, float]:
    cached = _rates_cache.get(base_code)
    if cached is not None and time.monotonic() - cached[1] < CACHE_TTL_SECONDS:
        return cached[0]

    async with (
        aiohttp.ClientSession() as session,
        session.get(RATES_API_URL.format(base=base_code)) as response,
    ):
        if response.status != 200:
            raise CurrencyError(f"сервис курсов валют недоступен (HTTP {response.status})")
        data = await response.json()

    if data.get("result") != "success":
        raise CurrencyError(f"не знаю валюту {base_code}")

    rates = data["rates"]
    _rates_cache[base_code] = (rates, time.monotonic())
    return rates


async def convert_currency(amount: float, from_code: str, to_code: str) -> float:
    rates = await _fetch_rates(from_code)
    rate = rates.get(to_code)
    if rate is None:
        raise CurrencyError(f"не знаю валюту {to_code}")
    return amount * rate
