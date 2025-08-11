from __future__ import annotations
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class ChannelItem(BaseModel):
  id: int
  title: Optional[str]
  username: Optional[str]
  total: int


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
  take_profits: list[float]
  original_text: str


class ChannelStats(BaseModel):
  channel_id: int
  title: Optional[str]
  username: Optional[str]
  total: int
  long_count: int
  short_count: int
  long_short_ratio: Optional[float]
  mean_leverage: Optional[float]
  mean_per_day: Optional[float]
  mean_per_week: Optional[float]


class SymbolStats(BaseModel):
  symbol: str
  total: int
  long_count: int
  short_count: int
  long_short_ratio: Optional[float]
  mean_leverage: Optional[float]
  mean_per_day: Optional[float]
  mean_per_week: Optional[float]
