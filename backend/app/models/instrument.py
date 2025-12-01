"""
Модель инструмента (тикера)
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
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
    index_id = Column(Integer, ForeignKey("indexes.id"), nullable=True)

    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    index = relationship("Index", back_populates="instruments")
    ohlcv_data = relationship("OHLCV", back_populates="instrument", cascade="all, delete-orphan")
    signals = relationship("Signal", back_populates="instrument", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Instrument(ticker='{self.ticker}', name='{self.name}', market='{self.market}')>"
