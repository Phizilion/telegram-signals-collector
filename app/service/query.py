from __future__ import annotations
from datetime import datetime
from sqlalchemy import select, func, case, Float
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Channel, Signal, TradeSide


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
    return [{"symbol": r.symbol, "total": int(r.total or 0)} for r in rows]


async def get_signals_by_channel(session: AsyncSession, channel_id: int, limit: int = 100, offset: int = 0) -> list[Signal]:
    q = (
        select(Signal)
        .where(Signal.channel_id == channel_id)
        .order_by(Signal.message_date.desc())
        .limit(limit)
        .offset(offset)
    )
    return list((await session.execute(q)).scalars().all())


async def get_signals_by_symbol(
    session: AsyncSession,
    symbol: str,
    limit: int = 100,
    offset: int = 0
) -> list[tuple[Signal, Channel]]:
    """
    Return signals for a symbol **joined with Channel** to avoid N+1 queries.
    """
    q = (
        select(Signal, Channel)
        .join(Channel, Signal.channel_id == Channel.id)
        .where(Signal.symbol == symbol.upper())
        .order_by(Signal.message_date.desc())
        .limit(limit)
        .offset(offset)
    )
    return list((await session.execute(q)).all())


async def stats_by_channel(session: AsyncSession) -> list[dict]:
    long_case = case((Signal.side == TradeSide.long, 1), else_=0)
    short_case = case((Signal.side == TradeSide.short, 1), else_=0)

    # average per week (calendar weeks) per channel using SQLite strftime('%Y-%W')
    weekly_counts = (
        select(
            Signal.channel_id.label("channel_id"),
            func.strftime("%Y-%W", Signal.message_date).label("wk"),
            func.count(Signal.id).label("cnt"),
        )
        .group_by(Signal.channel_id, "wk")
    ).subquery("wk_ch")

    avg_weekly = (
        select(
            weekly_counts.c.channel_id,
            func.avg(weekly_counts.c.cnt).label("avg_per_week"),
        )
        .group_by(weekly_counts.c.channel_id)
    ).subquery("avg_wk_ch")

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
            avg_weekly.c.avg_per_week,
        )
        .join(Signal, Signal.channel_id == Channel.id, isouter=True)
        .join(avg_weekly, avg_weekly.c.channel_id == Channel.id, isouter=True)
        .group_by(Channel.id)
    )

    rows = (await session.execute(q)).all()

    out: list[dict] = []
    for r in rows:
        total = int(r.total or 0)
        long_count = int(r.long_count or 0)
        short_count = int(r.short_count or 0)
        long_total_ratio = (long_count / total) if total else None

        per_day, _ = _per_day_week(total, r.first_dt, r.last_dt)
        per_week = float(r.avg_per_week) if r.avg_per_week is not None else None

        out.append({
            "channel_id": r.channel_id,
            "title": r.title,
            "username": r.username,
            "total": total,
            "long_count": long_count,
            "short_count": short_count,
            "long_total_ratio": long_total_ratio,
            "mean_leverage": float(r.mean_leverage) if r.mean_leverage is not None else None,
            "mean_per_day": per_day,
            "mean_per_week": round(per_week, 6) if per_week is not None else None,
        })
    return out


async def stats_by_symbol(session: AsyncSession) -> list[dict]:
    long_case = case((Signal.side == TradeSide.long, 1), else_=0)
    short_case = case((Signal.side == TradeSide.short, 1), else_=0)

    # average per week per symbol
    weekly_counts = (
        select(
            Signal.symbol.label("symbol"),
            func.strftime("%Y-%W", Signal.message_date).label("wk"),
            func.count(Signal.id).label("cnt"),
        )
        .group_by(Signal.symbol, "wk")
    ).subquery("wk_sym")

    avg_weekly = (
        select(
            weekly_counts.c.symbol,
            func.avg(weekly_counts.c.cnt).label("avg_per_week"),
        )
        .group_by(weekly_counts.c.symbol)
    ).subquery("avg_wk_sym")

    q = (
        select(
            Signal.symbol,
            func.count(Signal.id).label("total"),
            func.sum(long_case).label("long_count"),
            func.sum(short_case).label("short_count"),
            func.avg(Signal.leverage.cast(Float)).label("mean_leverage"),
            func.min(Signal.message_date).label("first_dt"),
            func.max(Signal.message_date).label("last_dt"),
            avg_weekly.c.avg_per_week,
        )
        .join(avg_weekly, avg_weekly.c.symbol == Signal.symbol, isouter=True)
        .group_by(Signal.symbol)
    )

    rows = (await session.execute(q)).all()

    out: list[dict] = []
    for r in rows:
        total = int(r.total or 0)
        long_count = int(r.long_count or 0)
        short_count = int(r.short_count or 0)
        long_total_ratio = (long_count / total) if total else None

        per_day, _ = _per_day_week(total, r.first_dt, r.last_dt)
        per_week = float(r.avg_per_week) if r.avg_per_week is not None else None

        out.append({
            "symbol": r.symbol,
            "total": total,
            "long_count": long_count,
            "short_count": short_count,
            "long_total_ratio": long_total_ratio,
            "mean_leverage": float(r.mean_leverage) if r.mean_leverage is not None else None,
            "mean_per_day": per_day,
            "mean_per_week": round(per_week, 6) if per_week is not None else None,
        })
    return out


def _per_day_week(total: int, first_dt: datetime | None, last_dt: datetime | None) -> tuple[float | None, float | None]:
    """Return mean per day (span-based). Weekly average is computed via calendar-week grouping elsewhere."""
    if not total or not first_dt or not last_dt:
        return None, None
    span_days = max(1.0, (last_dt - first_dt).total_seconds() / 86400.0)
    per_day = float(total) / span_days
    return round(per_day, 6), None
