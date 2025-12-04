"""
Модель валюты (ISO 4217)
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.models.database import Base


class Currency(Base):
    """Модель валюты"""

    __tablename__ = "currencies"

    id = Column(Integer, primary_key=True, index=True)

    # Код валюты ISO 4217 (RUB, USD, EUR) или тикер криптовалюты (BTC, ETH, USDT)
    code = Column(String(10), unique=True, nullable=False, index=True)

    # Цифровой код ISO 4217 (643 для RUB, 840 для USD)
    numeric_code = Column(String(3), nullable=True)

    # Название валюты
    name = Column(String(100), nullable=False)

    # Название на английском
    name_en = Column(String(100), nullable=True)

    # Символ валюты (₽, $, €, ¥)
    symbol = Column(String(10), nullable=True)

    # Количество десятичных знаков (обычно 2, для крипты может быть больше)
    decimal_places = Column(Integer, nullable=False, default=2)

    # Активна ли валюта
    is_active = Column(Integer, nullable=False, default=1)

    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    instruments = relationship("Instrument", back_populates="currency_rel")
    indexes = relationship("Index", back_populates="currency_rel")

    def __repr__(self) -> str:
        return f"<Currency(code='{self.code}', name='{self.name}', symbol='{self.symbol}')>"
