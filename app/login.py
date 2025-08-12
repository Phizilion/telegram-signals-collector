from __future__ import annotations
import asyncio
from pathlib import Path
from pyrogram import Client
from app.config import settings


async def main() -> None:
    Path(settings.session_dir).mkdir(parents=True, exist_ok=True)
    session_path = Path(settings.session_dir) / f"{settings.session_name}.session"
    print(f"Session file: {session_path}")

    async with Client(
        name=settings.session_name,
        api_id=settings.api_id,
        api_hash=settings.api_hash,
        workdir=settings.session_dir,
    ) as app:
        # touching storage ensures session written
        me = await app.get_me()
        print(f"Logged in as @{me.username or me.id}. Session saved.")


if __name__ == "__main__":
    asyncio.run(main())