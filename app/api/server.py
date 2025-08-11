from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ..db import init_db
from ..llm import LLMClient
from ..processor import Processor
from ..telegram_client import TelegramListener
from ..config import settings
from .routes import router


app = FastAPI(title="Telegram Signal Collector API", version="0.2.0")

# CORS: allow local dev and generic origins (adjust in production)
app.add_middleware(
  CORSMiddleware,
  allow_origins=[
    "*",  # set to specific domain(s) in production
    "http://localhost:5173",
    "http://127.0.0.1:5173",
  ],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

app.include_router(router)

# Shared objects for lifespan
_llm: LLMClient | None = None
_processor: Processor | None = None
_listener: TelegramListener | None = None


@app.on_event("startup")
async def on_startup() -> None:
  global _llm, _processor, _listener
  await init_db()
  _llm = LLMClient()
  _processor = Processor(llm=_llm, concurrency=settings.parser_concurrency)
  await _processor.start()
  _listener = TelegramListener(processor=_processor)
  await _listener.start()


@app.on_event("shutdown")
async def on_shutdown() -> None:
  global _processor, _listener
  if _listener:
    await _listener.stop()
  if _processor:
    await _processor.stop()
