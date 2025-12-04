"""
Модель инструмента (тикера)
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship

from app.models.database import Base


class Instrument(Base):
    """Модель финансового инструмента"""

    __tablename__ = "instruments"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    market = Column(String(50), nullable=False)  # MOEX, CME, etc.
    instrument_type = Column(String(50), nullable=False)  # stock, future, index

    # Связь с индексом
    index_id = Column(Integer, ForeignKey("indexes.id", ondelete="SET NULL"), nullable=True)

    # Связь с валютой
    currency_id = Column(Integer, ForeignKey("currencies.id", ondelete="SET NULL"), nullable=True, index=True)

    # Дополнительные поля
    isin = Column(String(12), nullable=True)  # Международный идентификатор
    board = Column(String(50), nullable=True)  # Режим торгов (TQBR, RFUD)
    lot_size = Column(Integer, nullable=True)  # Размер лота
    tick_size = Column(String(20), nullable=True)  # Шаг цены
    extra_data = Column(JSON, nullable=True)  # Дополнительная информация

    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    index = relationship("Index", back_populates="instruments")
    currency_rel = relationship("Currency", back_populates="instruments")
    ohlcv_data = relationship("OHLCV", back_populates="instrument", cascade="all, delete-orphan")
    signals = relationship("Signal", back_populates="instrument", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Instrument(ticker='{self.ticker}', name='{self.name}', market='{self.market}')>"
