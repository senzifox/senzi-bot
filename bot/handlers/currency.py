import logging
import math
import os
from uuid import uuid4

from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultCachedPhoto, Message
from aiohttp import ClientSession

from bot.access import AccessControlMiddleware
from bot.services.crypto import TICKER_TO_COINGECKO_ID
from bot.services.exchange import ExchangeError, convert

router = Router(name="currency")
router.message.middleware(AccessControlMiddleware())
router.inline_query.middleware(AccessControlMiddleware())

logger = logging.getLogger(__name__)

KNOWN_CURRENCY_CODES = frozenset(
    "AED AFN ALL AMD ANG AOA ARS AUD AWG AZN BAM BBD BDT BGN BHD BIF BMD BND BOB BRL "
    "BSD BTN BWP BYN BZD CAD CDF CHF CLP CNY COP CRC CUP CVE CZK DJF DKK DOP DZD EGP "
    "ERN ETB EUR FJD FKP GBP GEL GHS GIP GMD GNF GTQ GYD HKD HNL HTG HUF IDR ILS INR "
    "IQD IRR ISK JMD JOD JPY KES KGS KHR KMF KPW KRW KWD KYD KZT LAK LBP LKR LRD LSL "
    "LYD MAD MDL MGA MKD MMK MNT MOP MRU MUR MVR MWK MXN MYR MZN NAD NGN NIO NOK NPR "
    "NZD OMR PAB PEN PGK PHP PKR PLN PYG QAR RON RSD RUB RWF SAR SBD SCR SDG SEK SGD "
    "SHP SLE SOS SRD SSP STN SYP SZL THB TJS TMT TND TOP TRY TTD TWD TZS UAH UGX USD "
    "UYU UZS VES VND VUV WST XAF XCD XOF XPF YER ZAR ZMW ZWL".split()
)

KNOWN_CODES = KNOWN_CURRENCY_CODES | TICKER_TO_COINGECKO_ID.keys()


def _parse_amount(token: str) -> float:
    if "." in token or token.count(",") > 1:
        normalized = token.replace(",", "")
    else:
        normalized = token.replace(",", ".")
    value = float(normalized)
    if not math.isfinite(value):
        raise ValueError(f"not a finite number: {token}")
    return value


def parse_currency_query(text: str) -> tuple[float, str, str] | None:
    currency_tokens: list[str] = []
    amount_tokens: list[float] = []

    for token in text.split():
        upper = token.upper()
        if upper in KNOWN_CODES:
            currency_tokens.append(upper)
            continue
        if any(ch.isdigit() for ch in token):
            try:
                amount_tokens.append(_parse_amount(token))
            except ValueError:
                return None

    if len(currency_tokens) != 2 or len(amount_tokens) > 1:
        return None

    from_code, to_code = currency_tokens
    if from_code == to_code:
        return None

    amount = amount_tokens[0] if amount_tokens else 1.0
    return amount, from_code, to_code


def format_conversion(amount: float, from_code: str, to_code: str, result: float) -> str:
    return f"{amount:g} {from_code} = {result:.2f} {to_code}"


def currency_query(message: Message) -> dict[str, float | str] | bool:
    if not message.text:
        return False
    parsed = parse_currency_query(message.text)
    if not parsed:
        return False
    amount, from_code, to_code = parsed
    return {"amount": amount, "from_code": from_code, "to_code": to_code}


@router.message(currency_query)
async def handle_currency_message(
    message: Message, amount: float, from_code: str, to_code: str, http_session: ClientSession
) -> None:
    user_id = message.from_user.id if message.from_user else "?"
    logger.info("Конвертация от %s: %s %s -> %s", user_id, amount, from_code, to_code)
    try:
        result = await convert(http_session, amount, from_code, to_code)
        await message.answer_photo(
            photo=os.environ["CURRENCY_PLACEHOLDER_PHOTO_FILE_ID"],
            caption=format_conversion(amount, from_code, to_code, result),
        )
    except ExchangeError as e:
        logger.warning("Отказ по конвертации %s %s -> %s: %s", amount, from_code, to_code, e)
        await message.answer(f"Не удалось сконвертировать: {e}")
    except Exception:
        logger.exception("Ошибка конвертации %s %s -> %s", amount, from_code, to_code)
        await message.answer("Что-то сломалось на моей стороне")


def currency_inline_query(inline_query: InlineQuery) -> dict[str, float | str] | bool:
    parsed = parse_currency_query(inline_query.query)
    if not parsed:
        return False
    amount, from_code, to_code = parsed
    return {"amount": amount, "from_code": from_code, "to_code": to_code}


@router.inline_query(currency_inline_query)
async def handle_currency_inline_query(
    inline_query: InlineQuery,
    amount: float,
    from_code: str,
    to_code: str,
    http_session: ClientSession,
) -> None:
    logger.info(
        "Inline-конвертация от %s: %s %s -> %s",
        inline_query.from_user.id,
        amount,
        from_code,
        to_code,
    )
    try:
        result = await convert(http_session, amount, from_code, to_code)
        text = format_conversion(amount, from_code, to_code, result)
    except ExchangeError as e:
        logger.warning("Отказ по inline-конвертации %s %s -> %s: %s", amount, from_code, to_code, e)
        text = f"Не удалось сконвертировать: {e}"
    except Exception:
        logger.exception("Ошибка inline-конвертации %s %s -> %s", amount, from_code, to_code)
        text = "Что-то сломалось на моей стороне"

    await inline_query.answer(
        [
            InlineQueryResultCachedPhoto(
                id=uuid4().hex,
                photo_file_id=os.environ["CURRENCY_PLACEHOLDER_PHOTO_FILE_ID"],
                caption=text,
            )
        ],
        cache_time=60,
        is_personal=True,
    )
