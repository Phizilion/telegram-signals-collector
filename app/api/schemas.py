from __future__ import annotations
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class ChannelItem(BaseModel):
    id: int
    title: Optional[str]
    username: Optional[str]
    total: int
    deleted: int = Field(0, description="Number of deleted signals in channel")
    edited: int = Field(0, description="Number of edited signals in channel")


class SymbolItem(BaseModel):
    symbol: str = Field(..., description="Base symbol, e.g., BTC")
    total: int


class SignalItem(BaseModel):
    id: int
    channel_id: int
    message_id: int
    message_date: datetime
    symbol: str
    side: Literal["long", "short"]
    leverage: Optional[int] = None
    stop_loss: Optional[list[float]] = None
    take_profits: Optional[list[float]] = None
    original_text: str

    deleted: bool = False
    edited: bool = False

    # Optional channel info for symbols view
    channel_title: Optional[str] = None
    channel_username: Optional[str] = None


class ChannelStats(BaseModel):
    channel_id: int
    title: Optional[str]
    username: Optional[str]
    total: int
    long_count: int
    short_count: int
    long_total_ratio: Optional[float]
    mean_leverage: Optional[float]
    mean_per_day: Optional[float]
    mean_per_week: Optional[float]
    deleted: int
    edited: int


class SymbolStats(BaseModel):
    symbol: str
    total: int
    long_count: int
    short_count: int
    long_total_ratio: Optional[float]
    mean_leverage: Optional[float]
    mean_per_day: Optional[float]
    mean_per_week: Optional[float]


class EditionItem(BaseModel):
    text: str
    edited_at: datetime
