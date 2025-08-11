from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from enum import Enum


class TradeSide(str, Enum):
  long = "long"
  short = "short"


class Signal(BaseModel):
  id: int
  channel_id: int
  message_id: int
  message_date: datetime
  symbol: str
  side: TradeSide
  leverage: Optional[int] = None
  stop_loss: Optional[List[float]] = None
  take_profits: List[float]
  original_text: str

  class Config:
    orm_mode = True
