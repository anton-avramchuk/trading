"""
Модель результата бэктеста стратегии
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.models.database import Base


class Backtest(Base):
    """Модель результата бэктеста"""

    __tablename__ = "backtests"

    id = Column(Integer, primary_key=True, index=True)

    # Связь со стратегией
    strategy_id = Column(Integer, ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False, index=True)

    # Список инструментов (JSON array: ["GAZP", "SBER", "LKOH"])
    instruments = Column(JSON, nullable=False)

    # Таймфрейм
    timeframe_id = Column(Integer, ForeignKey("timeframes.id"), nullable=False, index=True)

    # Период бэктеста
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

    # Начальный капитал
    initial_capital = Column(Float, nullable=False)

    # Финальная стоимость портфеля
    final_capital = Column(Float, nullable=True)

    # Общая доходность (%)
    total_return = Column(Float, nullable=True)

    # Годовая доходность (%)
    annual_return = Column(Float, nullable=True)

    # Коэффициент Шарпа
    sharpe_ratio = Column(Float, nullable=True)

    # Максимальная просадка (%)
    max_drawdown = Column(Float, nullable=True)

    # Общее количество сделок
    total_trades = Column(Integer, nullable=True, default=0)

    # Прибыльные сделки
    winning_trades = Column(Integer, nullable=True, default=0)

    # Убыточные сделки
    losing_trades = Column(Integer, nullable=True, default=0)

    # Процент прибыльных сделок
    win_rate = Column(Float, nullable=True)

    # Средняя прибыльная сделка
    avg_win = Column(Float, nullable=True)

    # Средняя убыточная сделка
    avg_loss = Column(Float, nullable=True)

    # Profit Factor (avg_win / avg_loss)
    profit_factor = Column(Float, nullable=True)

    # Детальные метрики (JSON)
    metrics = Column(JSON, nullable=True)

    # Статус бэктеста (pending, running, completed, failed)
    status = Column(String(20), nullable=False, index=True, default="pending")

    # Временные метки
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)

    # Ошибка (если есть)
    error = Column(Text, nullable=True)

    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    strategy = relationship("Strategy", back_populates="backtests")
    timeframe_rel = relationship("Timeframe")

    def __repr__(self) -> str:
        return (
            f"<Backtest("
            f"strategy_id={self.strategy_id}, "
            f"status='{self.status}', "
            f"total_return={self.total_return}, "
            f"sharpe_ratio={self.sharpe_ratio}"
            f")>"
        )
