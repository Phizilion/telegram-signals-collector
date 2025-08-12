from __future__ import annotations
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  """Application configuration via env/.env."""

  # Telegram
  api_id: int = Field(..., alias="API_ID")
  api_hash: str = Field(..., alias="API_HASH")
  session_dir: str = Field(".pyrogram", alias="TELEGRAM_SESSION_DIR")
  session_name: str = Field("signals", alias="TELEGRAM_SESSION_NAME")

  # LLM
  openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
  openai_model: str = Field("gpt-4o-mini", alias="OPENAI_MODEL")
  rate_limit_per_minute: int = Field(30, alias="RATE_LIMIT_PER_MINUTE")
  parser_concurrency: int = Field(2, alias="PARSER_CONCURRENCY")

  # DB
  db_url: str = Field("sqlite+aiosqlite:///./signals.db", alias="DB_URL")

  # Logging
  log_level: str = Field("INFO", alias="LOG_LEVEL")

  model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()