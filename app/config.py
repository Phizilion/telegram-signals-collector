from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  model_config = SettingsConfigDict(env_file=".env", env_prefix="", case_sensitive=False)

  database_url: str = "sqlite+aiosqlite:///./signals.db"
  parser_concurrency: int = 4


settings = Settings()
