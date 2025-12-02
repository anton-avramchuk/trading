"""
Движок бэктестинга
"""
from datetime import date, datetime
from typing import Dict, List, Optional

import pandas as pd
from loguru import logger
from pydantic import BaseModel

from app.backtesting.order import OrderManager, OrderSide, OrderType
from app.backtesting.portfolio import Portfolio
from app.core.data_manager import DataManager
from app.signals.generator import SignalGenerator
from app.signals.risk_manager import RiskManager
from app.strategies.base import BaseStrategy, Signal


class Trade(BaseModel):
    """Завершённая сделка"""
    ticker: str
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    quantity: int
    side: str  # "LONG" или "SHORT"
    pnl: float
    pnl_percent: float
    commission: float
    reason: Optional[str] = None  # "SIGNAL", "STOP_LOSS", "TAKE_PROFIT"


class BacktestResult(BaseModel):
    """Результат бэктестинга"""
    strategy_name: str
    ticker: str
    start_date: str
    end_date: str
    initial_capital: float
    final_value: float
    total_return: float
    trades: List[Trade]
    equity_curve: List[Dict]

    class Config:
        arbitrary_types_allowed = True


class BacktestEngine:
    """
    Движок бэктестинга

    Выполняет полный цикл бэктестинга стратегии:
    - Генерация сигналов
    - Исполнение сделок
    - Управление портфелем
    - Обработка Stop Loss / Take Profit
    - Запись equity curve
    """

    def __init__(
        self,
        strategy: BaseStrategy,
        initial_capital: float = 100000.0,
        commission: float = 0.001,
        slippage: float = 0.0,
        use_risk_manager: bool = True
    ):
        """
        Инициализация движка

        Args:
            strategy: Торговая стратегия
            initial_capital: Начальный капитал
            commission: Комиссия (% от объёма)
            slippage: Проскальзывание (% от цены)
            use_risk_manager: Использовать риск-менеджер
        """
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage

        # Компоненты
        self.portfolio = Portfolio(
            initial_capital=initial_capital,
            commission=commission,
            slippage=slippage
        )
        self.order_manager = OrderManager()
        self.risk_manager = RiskManager() if use_risk_manager else None

        # Завершённые сделки
        self.completed_trades: List[Trade] = []

        # Статистика
        self.stats = {
            "signals_received": 0,
            "orders_created": 0,
            "orders_filled": 0,
            "stop_loss_triggered": 0,
            "take_profit_triggered": 0
        }

    def run(
        self,
        ticker: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> BacktestResult:
        """
        Запустить бэктестинг

        Args:
            ticker: Тикер инструмента
            start_date: Начальная дата
            end_date: Конечная дата

        Returns:
            BacktestResult: Результаты бэктестинга
        """
        logger.info(
            f"Starting backtest: strategy={self.strategy.name}, ticker={ticker}, "
            f"capital={self.initial_capital}"
        )

        # Сброс состояния
        self.portfolio.reset()
        self.completed_trades = []
        self.stats = {
            "signals_received": 0,
            "orders_created": 0,
            "orders_filled": 0,
            "stop_loss_triggered": 0,
            "take_profit_triggered": 0
        }

        # Загрузка данных
        timeframes = self.strategy.required_timeframes()
        logger.info(f"Loading data for timeframes: {timeframes}")

        data_manager = DataManager()
        multi_tf_data = data_manager.get_multi_timeframe_data(
            ticker=ticker,
            timeframes=timeframes,
            start_date=start_date,
            end_date=end_date
        )

        if not multi_tf_data:
            raise ValueError(f"No data found for {ticker}")

        # Определить базовый таймфрейм
        base_timeframe = min(
            timeframes,
            key=lambda tf: data_manager._get_timeframe_minutes(tf)
        )
        base_data = multi_tf_data[base_timeframe]

        logger.info(
            f"Base timeframe: {base_timeframe}, bars: {len(base_data)}"
        )

        # Основной цикл бэктестинга
        warm_up_bars = 100

        for i in range(warm_up_bars, len(base_data)):
            current_time = base_data.index[i]
            current_bar = base_data.iloc[i]

            # Текущие цены
            current_prices = {ticker: current_bar["close"]}

            # 1. Обработка активных позиций (Stop Loss / Take Profit)
            self._check_stop_conditions(
                ticker=ticker,
                current_time=current_time,
                current_bar=current_bar
            )

            # 2. Генерация сигнала
            data_slice = self._get_data_slice(
                multi_tf_data,
                i,
                base_timeframe
            )

            signal = self.strategy.generate_signal(data_slice, current_time)

            if signal:
                self.stats["signals_received"] += 1

                # Применить риск-менеджмент
                if self.risk_manager:
                    signal = self.risk_manager.apply_risk_management(
                        signal,
                        data_slice[base_timeframe]
                    )

                # Исполнить сигнал
                self._execute_signal(
                    signal=signal,
                    ticker=ticker,
                    current_time=current_time,
                    current_price=current_bar["close"]
                )

            # 3. Записать equity point
            self.portfolio.record_equity(current_time, current_prices)

            # Логирование прогресса
            if i % max(1, (len(base_data) - warm_up_bars) // 10) == 0:
                progress = (i - warm_up_bars) / (len(base_data) - warm_up_bars) * 100
                logger.info(
                    f"Progress: {progress:.1f}%, "
                    f"equity: {self.portfolio.get_total_value(current_prices):.2f}"
                )

        # Закрыть все открытые позиции в конце
        self._close_all_positions(
            ticker=ticker,
            current_time=base_data.index[-1],
            current_price=base_data.iloc[-1]["close"]
        )

        # Создать результат
        result = BacktestResult(
            strategy_name=self.strategy.name,
            ticker=ticker,
            start_date=str(base_data.index[warm_up_bars].date()),
            end_date=str(base_data.index[-1].date()),
            initial_capital=self.initial_capital,
            final_value=self.portfolio.equity_curve[-1].total_value,
            total_return=self.portfolio.get_total_return(),
            trades=self.completed_trades,
            equity_curve=[
                {
                    "timestamp": str(point.timestamp),
                    "total_value": point.total_value,
                    "cash": point.cash,
                    "positions_value": point.positions_value
                }
                for point in self.portfolio.equity_curve
            ]
        )

        logger.info(
            f"Backtest completed: {len(self.completed_trades)} trades, "
            f"return: {result.total_return:.2f}%"
        )

        return result

    def _execute_signal(
        self,
        signal: Signal,
        ticker: str,
        current_time: datetime,
        current_price: float
    ) -> None:
        """
        Исполнить торговый сигнал

        Args:
            signal: Торговый сигнал
            ticker: Тикер
            current_time: Текущее время
            current_price: Текущая цена
        """
        if signal.signal_type == "BUY":
            # Проверка наличия позиции
            if self.portfolio.has_position(ticker):
                logger.debug(f"Already have position in {ticker}, skipping BUY signal")
                return

            # Рассчитать количество
            position_size = signal.position_size or 0.1
            position_value = self.portfolio.cash * position_size
            quantity = int(position_value / current_price)

            if quantity <= 0:
                logger.debug(f"Quantity is 0, skipping BUY signal")
                return

            # Купить
            success = self.portfolio.buy(
                ticker=ticker,
                quantity=quantity,
                price=current_price,
                timestamp=current_time,
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit
            )

            if success:
                self.stats["orders_created"] += 1
                self.stats["orders_filled"] += 1

        elif signal.signal_type == "SELL":
            # Проверка наличия позиции
            if not self.portfolio.has_position(ticker):
                logger.debug(f"No position in {ticker}, skipping SELL signal")
                return

            position = self.portfolio.get_position(ticker)

            # Продать
            success = self.portfolio.sell(
                ticker=ticker,
                quantity=position.quantity,
                price=current_price,
                timestamp=current_time
            )

            if success:
                self.stats["orders_filled"] += 1

                # Записать завершённую сделку
                pnl = position.get_pnl(current_price)
                pnl_percent = position.get_pnl_percent(current_price)

                trade = Trade(
                    ticker=ticker,
                    entry_time=position.entry_time,
                    exit_time=current_time,
                    entry_price=position.entry_price,
                    exit_price=current_price,
                    quantity=position.quantity,
                    side="LONG",
                    pnl=pnl,
                    pnl_percent=pnl_percent,
                    commission=self.portfolio.commission * (
                        position.entry_price + current_price
                    ) * position.quantity,
                    reason="SIGNAL"
                )
                self.completed_trades.append(trade)

    def _check_stop_conditions(
        self,
        ticker: str,
        current_time: datetime,
        current_bar: pd.Series
    ) -> None:
        """
        Проверить условия Stop Loss / Take Profit

        Args:
            ticker: Тикер
            current_time: Текущее время
            current_bar: Текущая свеча (с open, high, low, close)
        """
        if not self.portfolio.has_position(ticker):
            return

        position = self.portfolio.get_position(ticker)
        high = current_bar["high"]
        low = current_bar["low"]
        close = current_bar["close"]

        # Проверка Stop Loss
        if position.stop_loss is not None:
            if low <= position.stop_loss:
                # Stop Loss сработал
                logger.info(
                    f"Stop Loss triggered for {ticker}: "
                    f"price {low:.2f} <= SL {position.stop_loss:.2f}"
                )

                self.portfolio.sell(
                    ticker=ticker,
                    quantity=position.quantity,
                    price=position.stop_loss,
                    timestamp=current_time
                )

                pnl = position.get_pnl(position.stop_loss)
                pnl_percent = position.get_pnl_percent(position.stop_loss)

                trade = Trade(
                    ticker=ticker,
                    entry_time=position.entry_time,
                    exit_time=current_time,
                    entry_price=position.entry_price,
                    exit_price=position.stop_loss,
                    quantity=position.quantity,
                    side="LONG",
                    pnl=pnl,
                    pnl_percent=pnl_percent,
                    commission=self.portfolio.commission * (
                        position.entry_price + position.stop_loss
                    ) * position.quantity,
                    reason="STOP_LOSS"
                )
                self.completed_trades.append(trade)
                self.stats["stop_loss_triggered"] += 1
                return

        # Проверка Take Profit
        if position.take_profit is not None:
            if high >= position.take_profit:
                # Take Profit сработал
                logger.info(
                    f"Take Profit triggered for {ticker}: "
                    f"price {high:.2f} >= TP {position.take_profit:.2f}"
                )

                self.portfolio.sell(
                    ticker=ticker,
                    quantity=position.quantity,
                    price=position.take_profit,
                    timestamp=current_time
                )

                pnl = position.get_pnl(position.take_profit)
                pnl_percent = position.get_pnl_percent(position.take_profit)

                trade = Trade(
                    ticker=ticker,
                    entry_time=position.entry_time,
                    exit_time=current_time,
                    entry_price=position.entry_price,
                    exit_price=position.take_profit,
                    quantity=position.quantity,
                    side="LONG",
                    pnl=pnl,
                    pnl_percent=pnl_percent,
                    commission=self.portfolio.commission * (
                        position.entry_price + position.take_profit
                    ) * position.quantity,
                    reason="TAKE_PROFIT"
                )
                self.completed_trades.append(trade)
                self.stats["take_profit_triggered"] += 1
                return

    def _close_all_positions(
        self,
        ticker: str,
        current_time: datetime,
        current_price: float
    ) -> None:
        """
        Закрыть все открытые позиции в конце бэктеста

        Args:
            ticker: Тикер
            current_time: Текущее время
            current_price: Текущая цена
        """
        if not self.portfolio.has_position(ticker):
            return

        position = self.portfolio.get_position(ticker)

        logger.info(f"Closing position in {ticker} at end of backtest")

        self.portfolio.sell(
            ticker=ticker,
            quantity=position.quantity,
            price=current_price,
            timestamp=current_time
        )

        pnl = position.get_pnl(current_price)
        pnl_percent = position.get_pnl_percent(current_price)

        trade = Trade(
            ticker=ticker,
            entry_time=position.entry_time,
            exit_time=current_time,
            entry_price=position.entry_price,
            exit_price=current_price,
            quantity=position.quantity,
            side="LONG",
            pnl=pnl,
            pnl_percent=pnl_percent,
            commission=self.portfolio.commission * (
                position.entry_price + current_price
            ) * position.quantity,
            reason="END_OF_BACKTEST"
        )
        self.completed_trades.append(trade)

    def _get_data_slice(
        self,
        multi_tf_data: Dict[str, pd.DataFrame],
        end_idx: int,
        base_timeframe: str
    ) -> Dict[str, pd.DataFrame]:
        """
        Получить срез данных до определённого индекса

        Args:
            multi_tf_data: Multi-timeframe данные
            end_idx: Индекс конечной точки
            base_timeframe: Базовый таймфрейм

        Returns:
            Dict[str, pd.DataFrame]: Срез данных
        """
        base_data = multi_tf_data[base_timeframe]
        current_time = base_data.index[end_idx]

        data_slice = {}
        for timeframe, df in multi_tf_data.items():
            slice_df = df[df.index <= current_time].copy()
            data_slice[timeframe] = slice_df

        return data_slice

    def get_stats(self) -> Dict:
        """Получить статистику бэктестинга"""
        return self.stats.copy()
