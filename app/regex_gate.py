from __future__ import annotations
import re

# Quick heuristic to reduce LLM calls while still using LLM for final decision/parse.

# Symbols like BTC, BTCUSDT, BTC-PERP
_SYMBOL = r"[A-Z]{2,15}(?:USDT|USD|PERP)?"

# Sides (EN/RU) and simple verb variants
# long/short/buy/sell, лонг/шорт, покупка/купить/покупаем, продажа/продаем/продать
_SIDE = r"\b(?:long|short|buy|sell|лонг|шорт|покуп(?:ка|аем|ать)|купить|продажа|прода(?:ем|ть))\b"

# Take profit keywords (EN/RU): tp, t/p, take profit, тейк, тейк профит, цель/цели, target/targets
_TP = r"\b(?:tp|t/p|take\s*profit|тейк(?:\s*профит)?|цели?|targets?)\b"

# Stop loss keywords (EN/RU): sl, s/l, stop loss, стоп, стоп лосс, стоплосс
_SL = r"\b(?:sl|s/l|stop\s*loss|стоп(?:\s*лосс)?|стоплосс)\b"

# Entry keywords (EN/RU): entry point, enter, вход, заходим
_ENTRY = r"\b(?:entry\s*point|enter|вход|заходим)\b"

# Leverage forms:
# - numeric with x: 10x, 25 x, x10
# - words + number: leverage 10, lev 10, плечо 10, кредитное плечо 10
_LEVERAGE = r"\b(?:(?:\d{1,3}\s*x|x\s*\d{1,3})|(?:lev(?:erage)?|плечо|кредитное\s*плечо)\s*:?\s*\d{1,3})\b"

# Price numbers (kept simple)
_PRICE = r"\d{1,5}(?:\.\d+)?"

_SYMBOL_RE = re.compile(_SYMBOL, re.I | re.U)
_SIDE_RE = re.compile(_SIDE, re.I | re.U)
_TP_RE = re.compile(_TP, re.I | re.U)
_SL_RE = re.compile(_SL, re.I | re.U)
_ENTRY_RE = re.compile(_ENTRY, re.I | re.U)
_LEVERAGE_RE = re.compile(_LEVERAGE, re.I | re.U)
_PRICE_RE = re.compile(_PRICE)


def looks_like_signal(text: str) -> bool:
    """
    Lightweight gate before LLM:
    - hits: symbol, side, TP, SL, entry keywords, leverage, price density
    - require at least 2 signals to pass (conservative)
    """
    if not text:
        return False

    hits = 0
    if _SYMBOL_RE.search(text):
        hits += 1
    if _SIDE_RE.search(text):
        hits += 1
    if _TP_RE.search(text):
        hits += 1
    if _SL_RE.search(text):
        hits += 1
    if _ENTRY_RE.search(text):
        hits += 1
    if _LEVERAGE_RE.search(text):
        hits += 1

    # Price lines often accompany TP/SL tables; count if there are several prices
    if len(_PRICE_RE.findall(text)) >= 3:
        hits += 1

    return hits >= 2  # conservative gate
