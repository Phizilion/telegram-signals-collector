from __future__ import annotations
from datetime import datetime
from typing import Annotated, Literal, Optional
from pydantic import BaseModel, Field, field_validator
import re


_SYMBOL_STRIP = re.compile(r"\s")
_SUFFIXES = (
    "USDT", "USD", "PERP", "-PERP", "_PERP", "/USDT", "-USDT", "_USDT",
)


class SignalFields(BaseModel):
    """Fields the LLM should output. Minimal required: symbol, side."""
    symbol: str = Field(..., description="Trading asset base symbol without USDT suffix, e.g., BTC")
    side: Literal["long", "short"] = Field(..., description="Side of trade - long (buy) or short (sell)")
    leverage: Optional[int] = Field(None, ge=1, le=200, description="Leverage of trade, e.g. 15, integer or None")
    stop_loss: Optional[list[float]] = Field(None, min_length=1, description="List of stop loss prices, e.g. [0.2, 0.1], list of floats or None")
    take_profits: Optional[list[float]] = Field(None, min_length=1, description="List of take profit prices, e.g. [0.4, 0.5], list of floats or None")

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, v: str) -> str:
        s = _SYMBOL_STRIP.sub("", v or "").upper()
        for suf in _SUFFIXES:
            if s.endswith(suf):
                s = s[: -len(suf)]
        # keep alnum only
        s = re.sub(r"[^A-Z0-9]", "", s)
        if not s:
            raise ValueError("empty symbol after normalization")
        return s


class PersistedSignal(BaseModel):
    """Full record that will be stored to DB after merging metadata."""
    channel_id: int
    message_id: int
    message_date: datetime

    symbol: str
    side: Literal["long", "short"]
    leverage: Optional[int] = None
    stop_loss: Optional[list[float]] = None
    take_profits: Optional[list[float]] = None

    original_text: str