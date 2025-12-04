"""
Модель логов загрузок MOEX (для IMOEX микросервиса)
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.models.database import Base


class DownloadLog(Base):
    """Модель логов загрузок данных с MOEX"""

    __tablename__ = "download_log"

    id = Column(Integer, primary_key=True, index=True)

    # Связь с инструментом
    instrument_id = Column(Integer, ForeignKey("instruments.id", ondelete="SET NULL"), nullable=True, index=True)

    # Связь с таймфреймом
    timeframe_id = Column(Integer, ForeignKey("timeframes.id"), nullable=True, index=True)

    # Для обратной совместимости
    ticker = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False)

    # MOEX параметры
    market = Column(String(50), nullable=False)  # stock, futures
    board = Column(String(50), nullable=False)  # TQBR, RFUD, etc.

    # Статус загрузки
    status = Column(
        String(20),
        nullable=False,
        index=True,
        default="pending"
    )  # pending, running, completed, failed

    # Результаты
    records_imported = Column(Integer, default=0)

    # Период загрузки
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)

    # Временные метки
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)

    # Ошибка (если есть)
    error = Column(Text, nullable=True)

    # Дополнительная информация в JSON
    metadata = Column(JSON, nullable=True)
    # Пример metadata:
    # {
    #     "pages_fetched": 5,
    #     "duplicates_skipped": 10,
    #     "moex_response_time": 1.2,
    #     "validation_errors": []
    # }

    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    instrument = relationship("Instrument")
    timeframe_rel = relationship("Timeframe")

    def __repr__(self) -> str:
        return (
            f"<DownloadLog("
            f"ticker='{self.ticker}', "
            f"timeframe='{self.timeframe}', "
            f"status='{self.status}', "
            f"records={self.records_imported}"
            f")>"
        )
