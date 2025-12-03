"""
API endpoints для бэктестинга
"""
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel, Field

from app.backtesting.engine import BacktestEngine
from app.backtesting.reporter import BacktestMetrics, BacktestReporter
from app.strategies.registry import strategy_registry

router = APIRouter()


# Pydantic схемы


class BacktestRequest(BaseModel):
    """Запрос на запуск бэктестинга"""
    strategy_name: str = Field(..., description="Название стратегии")
    ticker: str = Field(..., description="Тикер инструмента")
    start_date: Optional[date] = Field(None, description="Начальная дата")
    end_date: Optional[date] = Field(None, description="Конечная дата")
    initial_capital: float = Field(100000.0, gt=0, description="Начальный капитал")
    commission: float = Field(0.001, ge=0, le=0.1, description="Комиссия (%)")
    slippage: float = Field(0.0, ge=0, le=0.1, description="Проскальзывание (%)")
    use_risk_manager: bool = Field(True, description="Использовать риск-менеджер")


class CompareStrategiesRequest(BaseModel):
    """Запрос на сравнение стратегий"""
    strategies: List[str] = Field(..., description="Список стратегий для сравнения")
    ticker: str = Field(..., description="Тикер инструмента")
    start_date: Optional[date] = Field(None, description="Начальная дата")
    end_date: Optional[date] = Field(None, description="Конечная дата")
    initial_capital: float = Field(100000.0, gt=0, description="Начальный капитал")


class TradeResponse(BaseModel):
    """Ответ с информацией о сделке"""
    ticker: str
    entry_time: str
    exit_time: str
    entry_price: float
    exit_price: float
    quantity: int
    side: str
    pnl: float
    pnl_percent: float
    commission: float
    reason: Optional[str] = None


class BacktestResponse(BaseModel):
    """Ответ с результатами бэктестинга"""
    strategy_name: str
    ticker: str
    start_date: str
    end_date: str
    initial_capital: float
    final_value: float
    total_return: float
    metrics: BacktestMetrics
    trades: List[TradeResponse]
    equity_curve: List[dict]


# API Endpoints


@router.post("/run", response_model=BacktestResponse)
async def run_backtest(request: BacktestRequest):
    """
    Запустить бэктестинг стратегии

    Выполняет полный цикл бэктестинга:
    - Загружает исторические данные
    - Генерирует торговые сигналы
    - Симулирует исполнение сделок
    - Рассчитывает метрики производительности
    """
    logger.info(
        f"Running backtest: strategy={request.strategy_name}, "
        f"ticker={request.ticker}, capital={request.initial_capital}"
    )

    # Получить стратегию
    try:
        strategy_class = strategy_registry.get(request.strategy_name)
        strategy = strategy_class()
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Strategy '{request.strategy_name}' not found: {e}"
        )

    # Создать движок бэктестинга
    engine = BacktestEngine(
        strategy=strategy,
        initial_capital=request.initial_capital,
        commission=request.commission,
        slippage=request.slippage,
        use_risk_manager=request.use_risk_manager
    )

    # Запустить бэктестинг
    try:
        result = engine.run(
            ticker=request.ticker,
            start_date=request.start_date,
            end_date=request.end_date
        )
    except Exception as e:
        logger.error(f"Backtest failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Backtest execution failed: {e}"
        )

    # Рассчитать метрики
    reporter = BacktestReporter(result)
    metrics = reporter.generate_metrics()

    # Конвертировать trades
    trade_responses = [
        TradeResponse(
            ticker=trade.ticker,
            entry_time=str(trade.entry_time),
            exit_time=str(trade.exit_time),
            entry_price=trade.entry_price,
            exit_price=trade.exit_price,
            quantity=trade.quantity,
            side=trade.side,
            pnl=trade.pnl,
            pnl_percent=trade.pnl_percent,
            commission=trade.commission,
            reason=trade.reason
        )
        for trade in result.trades
    ]

    logger.info(
        f"Backtest completed: {len(result.trades)} trades, "
        f"return: {result.total_return:.2f}%"
    )

    return BacktestResponse(
        strategy_name=result.strategy_name,
        ticker=result.ticker,
        start_date=result.start_date,
        end_date=result.end_date,
        initial_capital=result.initial_capital,
        final_value=result.final_value,
        total_return=result.total_return,
        metrics=metrics,
        trades=trade_responses,
        equity_curve=result.equity_curve
    )


@router.post("/compare")
async def compare_strategies(request: CompareStrategiesRequest):
    """
    Сравнить несколько стратегий

    Запускает бэктестинг для нескольких стратегий на одинаковых данных
    и возвращает сравнительную таблицу метрик.
    """
    logger.info(
        f"Comparing {len(request.strategies)} strategies on {request.ticker}"
    )

    results = []

    for strategy_name in request.strategies:
        try:
            # Получить стратегию
            strategy_class = strategy_registry.get(strategy_name)
            strategy = strategy_class()

            # Запустить бэктестинг
            engine = BacktestEngine(
                strategy=strategy,
                initial_capital=request.initial_capital
            )

            result = engine.run(
                ticker=request.ticker,
                start_date=request.start_date,
                end_date=request.end_date
            )

            # Рассчитать метрики
            reporter = BacktestReporter(result)
            metrics = reporter.generate_metrics()

            results.append({
                "strategy_name": strategy_name,
                "total_return": result.total_return,
                "total_trades": len(result.trades),
                "win_rate": metrics.win_rate,
                "profit_factor": metrics.profit_factor,
                "max_drawdown": metrics.max_drawdown_percent,
                "sharpe_ratio": metrics.sharpe_ratio,
                "final_value": result.final_value
            })

        except Exception as e:
            logger.error(f"Failed to backtest {strategy_name}: {e}")
            results.append({
                "strategy_name": strategy_name,
                "error": str(e)
            })

    return {
        "ticker": ticker,
        "start_date": str(start_date) if start_date else None,
        "end_date": str(end_date) if end_date else None,
        "initial_capital": initial_capital,
        "results": results
    }


@router.get("/metrics/description")
async def get_metrics_description():
    """
    Получить описание всех метрик бэктестинга

    Возвращает словарь с описанием каждой метрики.
    """
    return {
        "total_return": "Общий return в % за весь период",
        "annualized_return": "Аннуализированный return в %",
        "total_trades": "Общее количество сделок",
        "winning_trades": "Количество прибыльных сделок",
        "losing_trades": "Количество убыточных сделок",
        "win_rate": "Процент прибыльных сделок",
        "total_pnl": "Общая прибыль/убыток",
        "avg_pnl": "Средняя прибыль/убыток на сделку",
        "avg_win": "Средняя прибыль на прибыльной сделке",
        "avg_loss": "Средний убыток на убыточной сделке",
        "profit_factor": "Отношение gross profit к gross loss",
        "largest_win": "Максимальная прибыль за одну сделку",
        "largest_loss": "Максимальный убыток за одну сделку",
        "max_drawdown": "Максимальная просадка (абсолютная)",
        "max_drawdown_percent": "Максимальная просадка в %",
        "sharpe_ratio": "Sharpe Ratio (риск-adjusted return)",
        "sortino_ratio": "Sortino Ratio (downside risk-adjusted return)",
        "calmar_ratio": "Calmar Ratio (return / max drawdown)",
        "avg_trade_duration_days": "Средняя длительность сделки в днях",
        "max_consecutive_wins": "Максимальная серия побед",
        "max_consecutive_losses": "Максимальная серия поражений",
        "expectancy": "Математическое ожидание прибыли на сделку",
        "recovery_factor": "Total return / Max drawdown",
        "ulcer_index": "Ulcer Index (мера downside risk)"
    }
