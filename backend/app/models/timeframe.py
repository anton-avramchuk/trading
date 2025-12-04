"""
Модель таймфрейма
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.database import Base


class Timeframe(Base):
    """Модель таймфрейма"""

    __tablename__ = "timeframes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False, index=True)  # 1m, 10m, 1h, 1d, 1w, 1M, 1Q
    name = Column(String(50), nullable=False)  # 1 минута, 10 минут, 1 час, 1 день и т.д.
    description = Column(Text, nullable=True)

    # Количество минут (для сортировки и вычислений)
    minutes = Column(Integer, nullable=False, index=True)

    # Соответствующий интервал MOEX ISS API
    moex_interval = Column(Integer, nullable=False)  # 1, 10, 60, 24, 7, 31, 4

    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Integer, default=1)  # 1 = active, 0 = inactive

    # Relationships
    ohlcv_data = relationship("OHLCV", back_populates="timeframe_rel")

    def __repr__(self) -> str:
        return f"<Timeframe(code='{self.code}', name='{self.name}', minutes={self.minutes})>"
