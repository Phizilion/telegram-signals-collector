from __future__ import annotations
from typing import AsyncIterator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from .config import settings


class Base(DeclarativeBase):
  pass


engine = create_async_engine(
  settings.db_url,
  echo=False,
  pool_pre_ping=True,
  future=True,
)

AsyncSessionLocal = async_sessionmaker(
  bind=engine,
  autoflush=False,
  expire_on_commit=False,
  class_=AsyncSession,
)


async def init_db() -> None:
  """Create tables if they don't exist."""
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)


# FastAPI dependency – plain async function that yields the session (NOT a contextmanager)
async def get_session() -> AsyncIterator[AsyncSession]:
  async with AsyncSessionLocal() as session:
    try:
      yield session
      await session.commit()
    except Exception:
      await session.rollback()
      raise
