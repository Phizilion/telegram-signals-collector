from __future__ import annotations
from typing import AsyncIterator, Iterable
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from app.config import settings


class Base(DeclarativeBase):
    pass


engine: AsyncEngine = create_async_engine(
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
    """Create tables if they don't exist and apply light migrations."""
    async with engine.begin() as conn:
        # Enforce FK for SQLite
        await conn.exec_driver_sql("PRAGMA foreign_keys=ON;")
        # Create all declared tables
        await conn.run_sync(Base.metadata.create_all)
        # Minimal in-place migrations for new columns on existing installs
        await _migrate_signals_add_columns(conn)


async def _migrate_signals_add_columns(conn) -> None:
    """
    SQLite-safe additive migrations for `signals`:
      - deleted BOOLEAN NOT NULL DEFAULT 0
      - edited  BOOLEAN NOT NULL DEFAULT 0
      - last_checked_time DATETIME NULL
    And ensure `signal_editions` table exists (handled by create_all).
    """
    # Inspect table columns
    res = await conn.exec_driver_sql("PRAGMA table_info('signals');")
    cols = {row[1] for row in res.all()}  # second field is column name

    stmts: list[str] = []
    if "deleted" not in cols:
        stmts.append("ALTER TABLE signals ADD COLUMN deleted INTEGER NOT NULL DEFAULT 0;")
    if "edited" not in cols:
        stmts.append("ALTER TABLE signals ADD COLUMN edited INTEGER NOT NULL DEFAULT 0;")
    if "last_checked_time" not in cols:
        stmts.append("ALTER TABLE signals ADD COLUMN last_checked_time TEXT NULL;")

    for s in stmts:
        await conn.exec_driver_sql(s)


# FastAPI dependency – plain async function that yields the session
async def get_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
