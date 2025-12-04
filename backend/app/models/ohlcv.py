"""
Модель OHLCV (свечных данных)
"""
from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Float, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.database import Base


class OHLCV(Base):
    """Модель OHLCV данных (свечи)"""

    __tablename__ = "ohlcv"

    id = Column(Integer, primary_key=True, index=True)

    # Связь с инструментом
    instrument_id = Column(Integer, ForeignKey("instruments.id", ondelete="CASCADE"), nullable=False, index=True)

    # Связь с таймфреймом
    timeframe_id = Column(Integer, ForeignKey("timeframes.id"), nullable=False, index=True)

    # Для обратной совместимости и быстрых запросов
    timeframe = Column(String(10), nullable=False, index=True)  # 1h, 1d, 1w, 1M

    # Время
    timestamp = Column(DateTime, nullable=False, index=True)

    # OHLCV данные
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=False)

    # Relationships
    instrument = relationship("Instrument", back_populates="ohlcv_data")
    timeframe_rel = relationship("Timeframe", back_populates="ohlcv_data")

    # Constraints
    __table_args__ = (
        UniqueConstraint('instrument_id', 'timeframe_id', 'timestamp', name='uq_instrument_timeframe_timestamp'),
        Index('idx_instrument_timeframe_time', 'instrument_id', 'timeframe_id', 'timestamp'),
    )

    def __repr__(self) -> str:
        return (
            f"<OHLCV("
            f"instrument_id={self.instrument_id}, "
            f"timeframe='{self.timeframe}', "
            f"timestamp='{self.timestamp}', "
            f"close={self.close}"
            f")>"
        )

    def validate_ohlc(self) -> bool:
        """
        Валидация корректности OHLC данных

        Returns:
            bool: True если данные корректны
        """
        if self.high < max(self.open, self.close):
            return False
        if self.low > min(self.open, self.close):
            return False
        if any(v <= 0 for v in [self.open, self.high, self.low, self.close]):
            return False
        return True
