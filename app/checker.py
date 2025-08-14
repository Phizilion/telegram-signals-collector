from __future__ import annotations
import asyncio
import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Iterable, List, Dict

from pyrogram import Client
from pyrogram.errors import RPCError
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import AsyncSessionLocal
from app.models import Signal, SignalEdition

log = logging.getLogger("sc.checker")


class MessageChecker:
    """
    Periodically check signals for deletion/edits:
      - For messages younger than 7 days: check at most hourly.
      - Older than 7 days: check at most every 72 hours.
    Every 30 minutes the loop selects candidates by last_checked_time and processes them.
    """

    def __init__(self, client: Client, interval_seconds: int = 1800) -> None:
        self.client = client
        self.interval = max(5, interval_seconds)
        self._task: asyncio.Task | None = None
        self._stop = asyncio.Event()

    async def start(self) -> None:
        if self._task:
            return
        self._task = asyncio.create_task(self._runner(), name="message-checker")

    async def stop(self) -> None:
        self._stop.set()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except Exception:
                pass
            self._task = None

    async def _runner(self) -> None:
        log.info("message checker started (interval=%s sec)", self.interval)
        while not self._stop.is_set():
            try:
                await self._cycle()
            except asyncio.CancelledError:
                break
            except Exception:
                log.exception("message checker cycle failed")
            await asyncio.wait([self._stop.wait()], timeout=self.interval)

    async def _cycle(self) -> None:
        now = datetime.now(timezone.utc)
        younger_than_7d = now - timedelta(days=7)
        hour_ago = now - timedelta(hours=1)
        hours72_ago = now - timedelta(hours=72)

        async with AsyncSessionLocal() as session:
            # Select non-deleted signals that need checking
            q = select(Signal).where(
                Signal.deleted.is_(False),
                or_(
                    and_(
                        Signal.message_date >= younger_than_7d,
                        or_(Signal.last_checked_time.is_(None), Signal.last_checked_time <= hour_ago),
                    ),
                    and_(
                        Signal.message_date < younger_than_7d,
                        or_(Signal.last_checked_time.is_(None), Signal.last_checked_time <= hours72_ago),
                    ),
                ),
            ).limit(2000)

            rows: list[Signal] = list((await session.execute(q)).scalars().all())

        if not rows:
            return

        # Group by channel_id to leverage bulk fetches
        by_channel: Dict[int, List[Signal]] = defaultdict(list)
        for s in rows:
            by_channel[s.channel_id].append(s)

        for channel_id, signals in by_channel.items():
            await self._check_channel_batch(channel_id, signals)

    async def _check_channel_batch(self, channel_id: int, signals: list[Signal]) -> None:
        # Process individually (simple & robust). Bulk fetching can be added later if desired.
        for s in signals:
            await self._check_one(s)

    async def _check_one(self, s: Signal) -> None:
        now = datetime.now(timezone.utc)
        try:
            msg = await self.client.get_messages(chat_id=s.channel_id, message_ids=s.message_id)
        except RPCError:
            # Consider deleted
            await self._mark_deleted(s.id, now)
            return
        except Exception:
            log.exception("checker: get_messages failed for ch=%s msg=%s", s.channel_id, s.message_id)
            # Do not update last_checked_time on unexpected error; try again next cycle.
            return

        # Message exists: compare content
        new_text = (msg.text or msg.caption or "").strip()
        edited_at = msg.edit_date
        original_changed = new_text and (new_text != (s.original_text or "").strip())

        if edited_at and original_changed:
            await self._mark_edited(s.id, new_text, edited_at)

        # Update last_checked_time even if nothing happened
        async with AsyncSessionLocal() as session:
            db_s = await session.get(Signal, s.id)
            if db_s:
                db_s.last_checked_time = now
                session.add(db_s)
                await session.commit()

    async def _mark_deleted(self, signal_id: int, ts: datetime) -> None:
        async with AsyncSessionLocal() as session:
            s = await session.get(Signal, signal_id)
            if not s:
                return
            s.deleted = True
            s.last_checked_time = ts
            session.add(s)
            await session.commit()
        log.info("checker: marked deleted signal_id=%s", signal_id)

    async def _mark_edited(self, signal_id: int, new_text: str, edited_at: datetime) -> None:
        async with AsyncSessionLocal() as session:
            s = await session.get(Signal, signal_id)
            if not s:
                return

            # Avoid duplicate edition rows with identical text and timestamp
            last = (
                await session.execute(
                    select(SignalEdition)
                    .where(SignalEdition.signal_id == signal_id)
                    .order_by(SignalEdition.edited_at.desc())
                    .limit(1)
                )
            ).scalars().first()

            if last and last.text == new_text and last.edited_at == edited_at:
                s.last_checked_time = datetime.now(timezone.utc)
                s.edited = True
                session.add(s)
                await session.commit()
                return

            edition = SignalEdition(signal_id=signal_id, text=new_text, edited_at=edited_at)
            s.edited = True
            s.last_checked_time = datetime.now(timezone.utc)
            session.add_all([s, edition])
            await session.commit()
        log.info("checker: recorded edition signal_id=%s at %s", signal_id, edited_at.isoformat())
