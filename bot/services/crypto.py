import aiohttp

COINGECKO_PRICE_URL = "https://api.coingecko.com/api/v3/simple/price"

TICKER_TO_COINGECKO_ID = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "USDT": "tether",
    "BNB": "binancecoin",
    "SOL": "solana",
    "XRP": "ripple",
    "USDC": "usd-coin",
    "DOGE": "dogecoin",
    "ADA": "cardano",
    "TRX": "tron",
    "TON": "the-open-network",
    "AVAX": "avalanche-2",
    "SHIB": "shiba-inu",
    "DOT": "polkadot",
    "LINK": "chainlink",
    "BCH": "bitcoin-cash",
    "LTC": "litecoin",
    "NEAR": "near",
    "MATIC": "matic-network",
    "UNI": "uniswap",
    "ICP": "internet-computer",
    "XLM": "stellar",
    "ETC": "ethereum-classic",
    "ATOM": "cosmos",
    "FIL": "filecoin",
    "APT": "aptos",
    "ARB": "arbitrum",
    "OP": "optimism",
    "HBAR": "hedera-hashgraph",
    "VET": "vechain",
    "IMX": "immutable-x",
    "MKR": "maker",
    "AAVE": "aave",
    "ALGO": "algorand",
    "GRT": "the-graph",
    "SAND": "the-sandbox",
    "MANA": "decentraland",
    "EGLD": "elrond-erd-2",
    "THETA": "theta-token",
    "XMR": "monero",
    "FTM": "fantom",
    "RNDR": "render-token",
    "INJ": "injective-protocol",
    "SUI": "sui",
    "KAS": "kaspa",
    "PEPE": "pepe",
}


class CryptoError(Exception):
    pass


async def get_usd_prices(coingecko_ids: list[str]) -> dict[str, float]:
    params = {"ids": ",".join(coingecko_ids), "vs_currencies": "usd"}

    async with (
        aiohttp.ClientSession() as session,
        session.get(COINGECKO_PRICE_URL, params=params) as response,
    ):
        if response.status != 200:
            raise CryptoError(f"сервис курсов крипты недоступен (HTTP {response.status})")
        data = await response.json()

    prices = {}
    for coingecko_id in coingecko_ids:
        entry = data.get(coingecko_id)
        if entry is None or "usd" not in entry:
            raise CryptoError(f"не знаю курс {coingecko_id}")
        prices[coingecko_id] = entry["usd"]
    return prices
