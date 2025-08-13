from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import AsyncSessionLocal
from app.models import Channel, Signal, TradeSide
from app.schemas import SignalFields, PersistedSignal
from app.regex_gate import looks_like_signal
from app.llm import LLMClient

log = logging.getLogger(__name__)


class MessageEnvelope:
    """Container for Telegram message attributes we rely on."""
    __slots__ = ("channel_id", "channel_title", "channel_username", "message_id", "message_date", "text")

    def __init__(
        self,
        channel_id: int,
        channel_title: Optional[str],
        channel_username: Optional[str],
        message_id: int,
        message_date: datetime,
        text: str,
    ) -> None:
        self.channel_id = channel_id
        self.channel_title = channel_title
        self.channel_username = channel_username
        self.message_id = message_id
        if message_date.tzinfo is None:
            message_date = message_date.replace(tzinfo=timezone.utc)
        self.message_date = message_date.astimezone(timezone.utc)
        self.text = text or ""


class Processor:
    """Inline pipeline (no queue): heuristics -> LLM classify -> LLM parse -> persist."""

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    async def process(self, env: MessageEnvelope) -> None:
        text = env.text.strip()
        if not text:
            return

        likely = looks_like_signal(text)
        is_sig = likely or await self.llm.is_signal(text)
        if not is_sig:
            log.debug("not a signal: channel=%s msg=%s", env.channel_id, env.message_id)
            await self._ensure_channel(env, last_message_id=env.message_id)
            return

        parsed = await self.llm.parse_signal(text)
        if not parsed:
            log.debug("LLM failed to parse signal: channel=%s msg=%s", env.channel_id, env.message_id)
            await self._ensure_channel(env, last_message_id=env.message_id)
            return

        await self._persist_signal(env, parsed)

    async def _ensure_channel(self, env: MessageEnvelope, last_message_id: Optional[int] = None) -> None:
        async with AsyncSessionLocal() as session:
            try:
                existing = await session.get(Channel, env.channel_id)
                if existing is None:
                    ch = Channel(
                        id=env.channel_id,
                        title=env.channel_title,
                        username=env.channel_username,
                        last_message_id=last_message_id,
                    )
                    session.add(ch)
                    await session.commit()
                    return

                updated = False
                if env.channel_title and existing.title != env.channel_title:
                    existing.title = env.channel_title
                    updated = True
                if env.channel_username and existing.username != env.channel_username:
                    existing.username = env.channel_username
                    updated = True
                if last_message_id and (
                    not existing.last_message_id or last_message_id > existing.last_message_id
                ):
                    existing.last_message_id = last_message_id
                    updated = True
                if updated:
                    session.add(existing)
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def _persist_signal(self, env: MessageEnvelope, parsed: SignalFields) -> None:
        record = PersistedSignal(
            channel_id=env.channel_id,
            message_id=env.message_id,
            message_date=env.message_date,
            symbol=parsed.symbol,
            side=parsed.side,
            leverage=parsed.leverage,
            stop_loss=parsed.stop_loss,
            take_profits=parsed.take_profits,
            original_text=env.text,
        )

        async with AsyncSessionLocal() as session:
            try:
                await self._ensure_channel(env, last_message_id=env.message_id)
                await self._insert_signal(session, record)
                await session.commit()
                log.info(
                    "stored signal: ch=%s msg=%s %s %s tp=%s sl=%s lev=%s",
                    record.channel_id,
                    record.message_id,
                    record.symbol,
                    record.side,
                    record.take_profits,
                    record.stop_loss,
                    record.leverage,
                )
            except IntegrityError:
                await session.rollback()
                # Duplicate message in same channel; ignore.
            except Exception:
                await session.rollback()
                raise

    @staticmethod
    async def _insert_signal(session: AsyncSession, rec: PersistedSignal) -> None:
        sig = Signal(
            channel_id=rec.channel_id,
            message_id=rec.message_id,
            message_date=rec.message_date,
            symbol=rec.symbol,
            side=TradeSide(rec.side),
            leverage=rec.leverage,
            stop_loss=rec.stop_loss,
            take_profits=rec.take_profits,
            original_text=rec.original_text,
        )
        session.add(sig)
        await session.flush()
