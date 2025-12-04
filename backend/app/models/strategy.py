"""
Модель стратегии
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.models.database import Base


class Strategy(Base):
    """Модель торговой стратегии"""

    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)

    # Основная информация
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Конфигурация стратегии (JSON)
    config = Column(JSON, nullable=False)
    # Пример config:
    # {
    #     "indicators": [
    #         {"name": "MA", "timeframe": "1d", "params": {"period": 50}},
    #         {"name": "RSI", "timeframe": "1h", "params": {"period": 14}}
    #     ],
    #     "rules": {
    #         "entry": "close > MA_1d AND RSI_1h < 30",
    #         "exit": "RSI_1h > 70"
    #     }
    # }

    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Статус
    is_active = Column(Integer, default=1)  # 1 = active, 0 = inactive

    # Relationships
    signals = relationship("Signal", back_populates="strategy")

    def __repr__(self) -> str:
        return f"<Strategy(name='{self.name}', active={bool(self.is_active)})>"
