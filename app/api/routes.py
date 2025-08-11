from __future__ import annotations
from typing import Sequence
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session
from ..models import Signal
from .schemas import ChannelItem, SymbolItem, SignalItem, ChannelStats, SymbolStats
from ..service.query import (
  list_channels_with_counts,
  list_symbols_with_counts,
  get_signals_by_channel,
  get_signals_by_symbol,
  stats_by_channel,
  stats_by_symbol,
)

router = APIRouter(prefix="/api", tags=["signals"])


@router.get("/health")
async def health() -> dict:
  return {"status": "ok"}


@router.get("/channels", response_model=list[ChannelItem])
async def channels(session: AsyncSession = Depends(get_session)):
  return await list_channels_with_counts(session)


@router.get("/symbols", response_model=list[SymbolItem])
async def symbols(session: AsyncSession = Depends(get_session)):
  return await list_symbols_with_counts(session)


@router.get("/channels/{channel_id}/signals", response_model=list[SignalItem])
async def signals_by_channel(
  channel_id: int,
  limit: int = Query(100, ge=1, le=500),
  offset: int = Query(0, ge=0),
  session: AsyncSession = Depends(get_session),
):
  rows: Sequence[Signal] = await get_signals_by_channel(session, channel_id, limit=limit, offset=offset)
  return [_to_signal_item(s) for s in rows]


@router.get("/symbols/{symbol}/signals", response_model=list[SignalItem])
async def signals_by_symbol(
  symbol: str,
  limit: int = Query(100, ge=1, le=500),
  offset: int = Query(0, ge=0),
  session: AsyncSession = Depends(get_session),
):
  rows: Sequence[Signal] = await get_signals_by_symbol(session, symbol, limit=limit, offset=offset)
  return [_to_signal_item(s) for s in rows]


@router.get("/stats/channels", response_model=list[ChannelStats])
async def channels_stats(session: AsyncSession = Depends(get_session)):
  return await stats_by_channel(session)


@router.get("/stats/symbols", response_model=list[SymbolStats])
async def symbols_stats(session: AsyncSession = Depends(get_session)):
  return await stats_by_symbol(session)


# --- helpers ---


def _to_signal_item(s: Signal) -> SignalItem:
  return SignalItem(
    id=s.id,
    channel_id=s.channel_id,
    message_id=s.message_id,
    message_date=s.message_date,
    symbol=s.symbol,
    side=s.side.value if hasattr(s.side, "value") else str(s.side),
    leverage=s.leverage,
    stop_loss=s.stop_loss,
    take_profits=s.take_profits,
    original_text=s.original_text,
  )
