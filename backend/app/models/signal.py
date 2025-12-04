"""
Модель торгового сигнала
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.database import Base


class Signal(Base):
    """Модель торгового сигнала"""

    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)

    # Связь с инструментом
    instrument_id = Column(Integer, ForeignKey("instruments.id", ondelete="CASCADE"), nullable=False, index=True)

    # Связь со стратегией
    strategy_id = Column(Integer, ForeignKey("strategies.id", ondelete="SET NULL"), nullable=True, index=True)

    # Для обратной совместимости
    strategy_name = Column(String(255), nullable=False, index=True)

    # Тип сигнала
    signal_type = Column(String(10), nullable=False)  # BUY, SELL

    # Время и цена
    timestamp = Column(DateTime, nullable=False, index=True)
    price = Column(Float, nullable=False)

    # Дополнительная информация
    confidence = Column(Float, nullable=True)  # Уверенность в сигнале (0-1)

    # Риск-менеджмент
    position_size = Column(Float, nullable=True)  # Размер позиции
    stop_loss = Column(Float, nullable=True)  # Стоп-лосс
    take_profit = Column(Float, nullable=True)  # Тейк-профит

    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    instrument = relationship("Instrument", back_populates="signals")
    strategy = relationship("Strategy", back_populates="signals")

    def __repr__(self) -> str:
        return (
            f"<Signal("
            f"instrument_id={self.instrument_id}, "
            f"type='{self.signal_type}', "
            f"strategy='{self.strategy_name}', "
            f"price={self.price}, "
            f"timestamp='{self.timestamp}'"
            f")>"
        )
