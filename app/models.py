from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    String,
    Integer,
    BigInteger,
    Boolean,
    DateTime,
    Text,
    JSON,
    Enum,
    UniqueConstraint,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base
import enum


class TradeSide(str, enum.Enum):
    long = "long"
    short = "short"


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Telegram channel id
    title: Mapped[Optional[str]] = mapped_column(String(255))
    username: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    is_monitored: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_message_id: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    signals: Mapped[List["Signal"]] = relationship(back_populates="channel", cascade="all,delete-orphan")


class Signal(Base):
    __tablename__ = "signals"
    __table_args__ = (
        UniqueConstraint("channel_id", "message_id", name="uq_channel_message"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id", ondelete="CASCADE"), index=True)
    message_id: Mapped[int] = mapped_column(Integer, index=True)
    message_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    symbol: Mapped[str] = mapped_column(String(50), index=True)
    side: Mapped[TradeSide] = mapped_column(Enum(TradeSide), index=True)
    leverage: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    stop_loss: Mapped[Optional[list[float]]] = mapped_column(JSON, nullable=True)
    take_profits: Mapped[list[float]] = mapped_column(JSON, nullable=False)

    original_text: Mapped[str] = mapped_column(Text, nullable=False)

    # New flags and housekeeping
    deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    edited: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_checked_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    channel: Mapped[Channel] = relationship(back_populates="signals")
    editions: Mapped[List["SignalEdition"]] = relationship(
        back_populates="signal", cascade="all,delete-orphan", passive_deletes=True
    )


class SignalEdition(Base):
    __tablename__ = "signal_editions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    signal_id: Mapped[int] = mapped_column(ForeignKey("signals.id", ondelete="CASCADE"), index=True, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    edited_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    signal: Mapped[Signal] = relationship(back_populates="editions")
