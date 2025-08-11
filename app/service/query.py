from __future__ import annotations
from datetime import datetime
from typing import Iterable
from sqlalchemy import select, func, case, Float
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Channel, Signal, TradeSide


async def list_channels_with_counts(session: AsyncSession) -> list[dict]:
  q = (
    select(
      Channel.id,
      Channel.title,
      Channel.username,
      func.count(Signal.id).label("total")
    )
    .join(Signal, Signal.channel_id == Channel.id, isouter=True)
    .group_by(Channel.id)
    .order_by(func.count(Signal.id).desc())
  )
  rows = (await session.execute(q)).all()
  return [
    {"id": r.id, "title": r.title, "username": r.username, "total": int(r.total or 0)}
    for r in rows
  ]


async def list_symbols_with_counts(session: AsyncSession) -> list[dict]:
  q = (
    select(
      Signal.symbol,
      func.count(Signal.id).label("total")
    )
    .group_by(Signal.symbol)
    .order_by(func.count(Signal.id).desc())
  )
  rows = (await session.execute(q)).all()
  return [
    {"symbol": r.symbol, "total": int(r.total or 0)}
    for r in rows
  ]


async def get_signals_by_channel(session: AsyncSession, channel_id: int, limit: int = 100, offset: int = 0) -> list[Signal]:
  q = (
    select(Signal)
    .where(Signal.channel_id == channel_id)
    .order_by(Signal.message_date.desc())
    .limit(limit)
    .offset(offset)
  )
  return list((await session.execute(q)).scalars().all())


async def get_signals_by_symbol(session: AsyncSession, symbol: str, limit: int = 100, offset: int = 0) -> list[Signal]:
  q = (
    select(Signal)
    .where(Signal.symbol == symbol.upper())
    .order_by(Signal.message_date.desc())
    .limit(limit)
    .offset(offset)
  )
  return list((await session.execute(q)).scalars().all())


async def stats_by_channel(session: AsyncSession) -> list[dict]:
  long_case = case((Signal.side == TradeSide.long, 1), else_=0)
  short_case = case((Signal.side == TradeSide.short, 1), else_=0)

  q = (
    select(
      Channel.id.label("channel_id"),
      Channel.title,
      Channel.username,
      func.count(Signal.id).label("total"),
      func.sum(long_case).label("long_count"),
      func.sum(short_case).label("short_count"),
      func.avg(Signal.leverage.cast(Float)).label("mean_leverage"),
      func.min(Signal.message_date).label("first_dt"),
      func.max(Signal.message_date).label("last_dt"),
    )
    .join(Signal, Signal.channel_id == Channel.id, isouter=True)
    .group_by(Channel.id)
  )
  rows = (await session.execute(q)).all()

  out: list[dict] = []
  for r in rows:
    total = int(r.total or 0)
    long_count = int(r.long_count or 0)
    short_count = int(r.short_count or 0)
    ratio = (long_count / short_count) if short_count else None

    per_day, per_week = _per_day_week(total, r.first_dt, r.last_dt)

    out.append({
      "channel_id": r.channel_id,
      "title": r.title,
      "username": r.username,
      "total": total,
      "long_count": long_count,
      "short_count": short_count,
      "long_short_ratio": ratio,
      "mean_leverage": float(r.mean_leverage) if r.mean_leverage is not None else None,
      "mean_per_day": per_day,
      "mean_per_week": per_week,
    })
  return out


async def stats_by_symbol(session: AsyncSession) -> list[dict]:
  long_case = case((Signal.side == TradeSide.long, 1), else_=0)
  short_case = case((Signal.side == TradeSide.short, 1), else_=0)

  q = (
    select(
      Signal.symbol,
      func.count(Signal.id).label("total"),
      func.sum(long_case).label("long_count"),
      func.sum(short_case).label("short_count"),
      func.avg(Signal.leverage.cast(Float)).label("mean_leverage"),
      func.min(Signal.message_date).label("first_dt"),
      func.max(Signal.message_date).label("last_dt"),
    )
    .group_by(Signal.symbol)
  )
  rows = (await session.execute(q)).all()

  out: list[dict] = []
  for r in rows:
    total = int(r.total or 0)
    long_count = int(r.long_count or 0)
    short_count = int(r.short_count or 0)
    ratio = (long_count / short_count) if short_count else None
    per_day, per_week = _per_day_week(total, r.first_dt, r.last_dt)

    out.append({
      "symbol": r.symbol,
      "total": total,
      "long_count": long_count,
      "short_count": short_count,
      "long_short_ratio": ratio,
      "mean_leverage": float(r.mean_leverage) if r.mean_leverage is not None else None,
      "mean_per_day": per_day,
      "mean_per_week": per_week,
    })
  return out


def _per_day_week(total: int, first_dt: datetime | None, last_dt: datetime | None) -> tuple[float | None, float | None]:
  if not total or not first_dt or not last_dt:
    return None, None
  span_seconds = max(1.0, (last_dt - first_dt).total_seconds())
  per_day = float(total) / (span_seconds / 86400.0)
  per_week = per_day * 7.0
  return round(per_day, 6), round(per_week, 6)
