from __future__ import annotations
import logging
from pathlib import Path
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
from app.processor import Processor, MessageEnvelope
from app.config import settings

log = logging.getLogger(__name__)


class TelegramListener:
    """Wire Pyrogram events to the processing pipeline (inline, no queue)."""

    def __init__(self, processor: Processor) -> None:
        self.processor = processor
        Path(settings.session_dir).mkdir(parents=True, exist_ok=True)
        self._session_path = Path(settings.session_dir) / f"{settings.session_name}.session"

        self.client = Client(
            name=settings.session_name,
            api_id=settings.api_id,
            api_hash=settings.api_hash,
            workdir=settings.session_dir,
            in_memory=False,
        )

    async def start(self) -> None:
        if not self._session_path.exists():
            raise RuntimeError(
                f"Telegram session not found at '{self._session_path}'. Run `python -m app.login` to sign in."
            )

        self.client.add_handler(MessageHandler(self._on_channel_message, filters.channel))
        await self.client.start()
        log.info("pyrogram client started (session: %s)", self._session_path)

    async def stop(self) -> None:
        await self.client.stop()

    async def _on_channel_message(self, client: Client, message: Message) -> None:  # type: ignore[override]
        if not message or not message.chat or not message.chat.type.name.lower().startswith("channel"):
            return

        text = (message.text or message.caption or "").strip()
        if not text:
            return

        env = MessageEnvelope(
            channel_id=message.chat.id,
            channel_title=message.chat.title,
            channel_username=message.chat.username,
            message_id=message.id,
            message_date=message.date,
            text=text,
        )

        # Process inline (no queue/backpressure)
        await self.processor.process(env)
