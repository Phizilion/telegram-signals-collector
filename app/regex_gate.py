from __future__ import annotations
import re

# Quick heuristic to reduce LLM calls while still using LLM for final decision/parse.
_SYMBOL = r"[A-Z]{2,15}(?:USDT|USD|PERP)?"
_SIDE = r"\b(long|short|buy|sell)\b"
_TP = r"\b(?:tp|take\s*profit)s?\b"
_SL = r"\b(?:sl|stop\s*loss)\b"
_PRICE = r"\d{1,5}(?:\.\d+)?"

_SYMBOL_RE = re.compile(_SYMBOL, re.I)
_SIDE_RE = re.compile(_SIDE, re.I)
_TP_RE = re.compile(_TP, re.I)
_SL_RE = re.compile(_SL, re.I)
_PRICE_RE = re.compile(_PRICE)


def looks_like_signal(text: str) -> bool:
  if not text:
    return False
  hits = 0
  if _SYMBOL_RE.search(text):
    hits += 1
  if _SIDE_RE.search(text):
    hits += 1
  if _TP_RE.search(text):
    hits += 1
  # price lines often accompany TP/SL tables
  if _SL_RE.search(text) or len(_PRICE_RE.findall(text)) >= 3:
    hits += 1
  return hits >= 2  # conservative gate