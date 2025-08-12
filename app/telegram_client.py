from __future__ import annotations
import asyncio
import logging
from pathlib import Path
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
from .processor import Processor, MessageEnvelope
from .config import settings

log = logging.getLogger(__name__)


class TelegramListener:
    """Wire Pyrogram events to the processing pipeline."""

    def __init__(self, processor: Processor) -> None:
        self.processor = processor

        # Ensure session dir exists
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
        # Do not block FastAPI startup with interactive login; instruct user to run app.login
        if not self._session_path.exists():
            raise RuntimeError(
                f"Telegram session not found at '{self._session_path}'. Run `python -m app.login` to sign in."
            )

        # Register handler once client exists
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

        try:
            await self.processor.submit(env)
        except asyncio.QueueFull:
            log.warning("processor queue full; dropping message ch=%s msg=%s", env.channel_id, env.message_id)