from __future__ import annotations
from typing import Sequence, Any, Tuple, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session
from ..models import Signal, Channel
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
async def symbols_signals(
    symbol: str,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    # Service returns a result set from a joined query (Signal, Channel)
    rows: Sequence[Any] = await get_signals_by_symbol(session, symbol, limit=limit, offset=offset)

    out: list[SignalItem] = []
    for row in rows:
        s: Optional[Signal] = None
        ch: Optional[Channel] = None

        # SQLAlchemy 2.0 Row supports tuple-style indexing
        if hasattr(row, "__iter__") and not isinstance(row, Signal):
            try:
                s = row[0]  # type: ignore[index]
                ch = row[1]  # type: ignore[index]
            except Exception:
                pass

        if s is None:
            # Fallback for legacy scalar rows
            s = row  # type: ignore[assignment]

        if ch is None:
            # Ensure channel is present (avoids missing names in Symbols view)
            ch = await session.get(Channel, s.channel_id)

        out.append(_to_signal_item(s, ch))
    return out


@router.get("/stats/channels", response_model=list[ChannelStats])
async def channels_stats(session: AsyncSession = Depends(get_session)):
    return await stats_by_channel(session)


@router.get("/stats/symbols", response_model=list[SymbolStats])
async def symbols_stats(session: AsyncSession = Depends(get_session)):
    return await stats_by_symbol(session)


# --- helpers ---

def _to_signal_item(s: Signal, ch: Channel | None = None) -> SignalItem:
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
        channel_title=(ch.title if ch else None),
        channel_username=(ch.username if ch else None),
    )
