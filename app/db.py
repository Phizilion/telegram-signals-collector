from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from .config import settings


class Base(DeclarativeBase):
  pass


def _create_engine():
  return create_async_engine(settings.database_url, future=True)


engine = _create_engine()
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def init_db() -> None:
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
  async with AsyncSessionLocal() as session:
    yield session
