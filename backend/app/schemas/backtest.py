"""
Pydantic схемы для бэктестинга
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class BacktestConfig(BaseModel):
    """Конфигурация бэктеста"""

    strategy_id: int = Field(..., description="ID стратегии")
    tickers: List[str] = Field(..., min_length=1, description="Список тикеров")
    start_date: datetime = Field(..., description="Начальная дата")
    end_date: datetime = Field(..., description="Конечная дата")
    initial_capital: float = Field(100000.0, gt=0, description="Начальный капитал")
    commission: float = Field(0.0005, ge=0, le=1, description="Комиссия (доля)")


class Trade(BaseModel):
    """Сделка в бэктесте"""

    ticker: str = Field(..., description="Тикер")
    signal_type: str = Field(..., description="Тип сигнала (BUY, SELL)")
    entry_date: datetime = Field(..., description="Дата входа")
    entry_price: float = Field(..., gt=0, description="Цена входа")
    exit_date: Optional[datetime] = Field(None, description="Дата выхода")
    exit_price: Optional[float] = Field(None, gt=0, description="Цена выхода")
    quantity: int = Field(..., gt=0, description="Количество")
    pnl: Optional[float] = Field(None, description="Прибыль/убыток")
    pnl_percent: Optional[float] = Field(None, description="P&L в процентах")
    commission_paid: float = Field(0.0, ge=0, description="Уплаченная комиссия")
    is_open: bool = Field(True, description="Открыта ли позиция")


class EquityCurvePoint(BaseModel):
    """Точка equity curve"""

    timestamp: datetime = Field(..., description="Время")
    equity: float = Field(..., gt=0, description="Капитал")
    drawdown: float = Field(0.0, ge=0, description="Просадка")


class BacktestMetrics(BaseModel):
    """Метрики бэктеста"""

    # Основные метрики
    total_return: float = Field(..., description="Общая доходность (%)")
    annualized_return: float = Field(..., description="Годовая доходность (%)")
    sharpe_ratio: Optional[float] = Field(None, description="Коэффициент Шарпа")
    max_drawdown: float = Field(..., ge=0, description="Максимальная просадка (%)")

    # Метрики сделок
    total_trades: int = Field(..., ge=0, description="Всего сделок")
    winning_trades: int = Field(..., ge=0, description="Прибыльных сделок")
    losing_trades: int = Field(..., ge=0, description="Убыточных сделок")
    win_rate: float = Field(..., ge=0, le=100, description="Процент прибыльных сделок")

    # Финансовые метрики
    profit_factor: Optional[float] = Field(None, gt=0, description="Фактор прибыли")
    avg_win: float = Field(0.0, description="Средняя прибыль")
    avg_loss: float = Field(0.0, description="Средний убыток")
    avg_trade_duration: Optional[float] = Field(None, description="Средняя длительность сделки (дней)")

    # Капитал
    initial_capital: float = Field(..., gt=0, description="Начальный капитал")
    final_capital: float = Field(..., gt=0, description="Конечный капитал")
    total_commission: float = Field(0.0, ge=0, description="Общая комиссия")


class BacktestResult(BaseModel):
    """Результат бэктеста"""

    backtest_id: Optional[int] = Field(None, description="ID бэктеста")
    strategy_id: int = Field(..., description="ID стратегии")
    strategy_name: str = Field(..., description="Название стратегии")
    config: BacktestConfig = Field(..., description="Конфигурация бэктеста")
    metrics: BacktestMetrics = Field(..., description="Метрики")
    trades: List[Trade] = Field(default_factory=list, description="Список сделок")
    equity_curve: List[EquityCurvePoint] = Field(default_factory=list, description="Equity curve")
    created_at: Optional[datetime] = Field(None, description="Время создания")


class BacktestRunRequest(BaseModel):
    """Запрос на запуск бэктеста"""

    strategy_id: int = Field(..., description="ID стратегии")
    tickers: List[str] = Field(..., min_length=1, max_length=10, description="Список тикеров")
    start_date: datetime = Field(..., description="Начальная дата")
    end_date: datetime = Field(..., description="Конечная дата")
    initial_capital: float = Field(100000.0, gt=0, le=10000000, description="Начальный капитал")
    commission: float = Field(0.0005, ge=0, le=0.1, description="Комиссия (доля)")


class BacktestRunResponse(BaseModel):
    """Ответ на запуск бэктеста"""

    backtest_id: int = Field(..., description="ID бэктеста")
    status: str = Field(..., description="Статус (running, completed, failed)")
    message: Optional[str] = Field(None, description="Сообщение")


class BacktestListItem(BaseModel):
    """Элемент списка бэктестов"""

    backtest_id: int
    strategy_name: str
    tickers: List[str]
    start_date: datetime
    end_date: datetime
    total_return: float
    sharpe_ratio: Optional[float]
    max_drawdown: float
    total_trades: int
    created_at: datetime


class BacktestListResponse(BaseModel):
    """Список бэктестов"""

    backtests: List[BacktestListItem]
    total: int
