from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.llm import LLMClient
from app.log import setup_logging
from app.processor import Processor
from app.telegram_client import TelegramListener
from app.api.routes import router
from app.checker import MessageChecker

setup_logging()
log = logging.getLogger("sc.api")

app = FastAPI(title="Telegram Signal Collector API", version="0.3.2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

_llm: LLMClient | None = None
_processor: Processor | None = None
_listener: TelegramListener | None = None
_checker: MessageChecker | None = None


@app.on_event("startup")
async def on_startup() -> None:
    global _llm, _processor, _listener, _checker
    _llm = LLMClient()
    _processor = Processor(llm=_llm)
    _listener = TelegramListener(processor=_processor)
    await _listener.start()

    # Start periodic deletion/edition checker (every 30 minutes)
    _checker = MessageChecker(client=_listener.client, interval_seconds=1800)
    await _checker.start()

    log.info("Server start")


@app.on_event("shutdown")
async def on_shutdown() -> None:
    global _listener, _checker
    if _checker:
        await _checker.stop()
    if _listener:
        await _listener.stop()

    log.info("Server stop")
