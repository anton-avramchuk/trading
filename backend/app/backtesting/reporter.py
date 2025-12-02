"""
Генератор отчётов по бэктестингу
"""
import math
from typing import Dict, List, Optional

import numpy as np
from pydantic import BaseModel

from app.backtesting.engine import BacktestResult, Trade
from app.backtesting.portfolio import EquityPoint


class BacktestMetrics(BaseModel):
    """Метрики бэктестинга"""
    # Общие метрики
    total_return: float
    annualized_return: Optional[float] = None
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float

    # Метрики прибыльности
    total_pnl: float
    avg_pnl: float
    avg_win: float
    avg_loss: float
    profit_factor: Optional[float] = None
    largest_win: float
    largest_loss: float

    # Метрики риска
    max_drawdown: float
    max_drawdown_percent: float
    sharpe_ratio: Optional[float] = None
    sortino_ratio: Optional[float] = None
    calmar_ratio: Optional[float] = None

    # Метрики времени
    avg_trade_duration_days: Optional[float] = None
    max_consecutive_wins: int
    max_consecutive_losses: int

    # Дополнительные метрики
    expectancy: float
    recovery_factor: Optional[float] = None
    ulcer_index: Optional[float] = None


class BacktestReporter:
    """
    Генератор отчётов и расчёт метрик бэктестинга

    Рассчитывает все основные метрики:
    - Total Return, Annualized Return
    - Sharpe Ratio, Sortino Ratio
    - Max Drawdown
    - Win Rate, Profit Factor
    - И многое другое
    """

    def __init__(self, result: BacktestResult):
        """
        Инициализация репортера

        Args:
            result: Результат бэктестинга
        """
        self.result = result

    def generate_metrics(self) -> BacktestMetrics:
        """
        Сгенерировать все метрики

        Returns:
            BacktestMetrics: Полный набор метрик
        """
        trades = self.result.trades
        equity_curve = self.result.equity_curve

        if not trades:
            # Нет сделок - вернуть нулевые метрики
            return BacktestMetrics(
                total_return=0.0,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
                total_pnl=0.0,
                avg_pnl=0.0,
                avg_win=0.0,
                avg_loss=0.0,
                largest_win=0.0,
                largest_loss=0.0,
                max_drawdown=0.0,
                max_drawdown_percent=0.0,
                expectancy=0.0,
                max_consecutive_wins=0,
                max_consecutive_losses=0
            )

        # Базовые метрики
        total_return = self.result.total_return
        total_trades = len(trades)

        winning_trades = [t for t in trades if t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl < 0]

        win_count = len(winning_trades)
        loss_count = len(losing_trades)
        win_rate = (win_count / total_trades) * 100 if total_trades > 0 else 0.0

        # Прибыль/убыток
        total_pnl = sum(t.pnl for t in trades)
        avg_pnl = total_pnl / total_trades if total_trades > 0 else 0.0

        avg_win = (
            sum(t.pnl for t in winning_trades) / win_count
            if win_count > 0 else 0.0
        )
        avg_loss = (
            sum(t.pnl for t in losing_trades) / loss_count
            if loss_count > 0 else 0.0
        )

        largest_win = max((t.pnl for t in trades), default=0.0)
        largest_loss = min((t.pnl for t in trades), default=0.0)

        # Profit Factor
        gross_profit = sum(t.pnl for t in winning_trades)
        gross_loss = abs(sum(t.pnl for t in losing_trades))
        profit_factor = (
            gross_profit / gross_loss
            if gross_loss > 0 else None
        )

        # Expectancy
        expectancy = (
            (win_rate / 100) * avg_win - ((100 - win_rate) / 100) * abs(avg_loss)
        )

        # Drawdown
        max_dd, max_dd_pct = self._calculate_max_drawdown(equity_curve)

        # Risk metrics
        sharpe = self._calculate_sharpe_ratio(equity_curve)
        sortino = self._calculate_sortino_ratio(equity_curve)
        calmar = self._calculate_calmar_ratio(total_return, max_dd_pct)

        # Annualized return
        annualized_return = self._calculate_annualized_return(equity_curve, total_return)

        # Consecutive wins/losses
        max_consec_wins, max_consec_losses = self._calculate_consecutive_streaks(trades)

        # Avg trade duration
        avg_duration = self._calculate_avg_trade_duration(trades)

        # Recovery Factor
        recovery_factor = (
            total_return / abs(max_dd_pct)
            if max_dd_pct != 0 else None
        )

        # Ulcer Index
        ulcer = self._calculate_ulcer_index(equity_curve)

        return BacktestMetrics(
            total_return=round(total_return, 2),
            annualized_return=round(annualized_return, 2) if annualized_return else None,
            total_trades=total_trades,
            winning_trades=win_count,
            losing_trades=loss_count,
            win_rate=round(win_rate, 2),
            total_pnl=round(total_pnl, 2),
            avg_pnl=round(avg_pnl, 2),
            avg_win=round(avg_win, 2),
            avg_loss=round(avg_loss, 2),
            profit_factor=round(profit_factor, 2) if profit_factor else None,
            largest_win=round(largest_win, 2),
            largest_loss=round(largest_loss, 2),
            max_drawdown=round(max_dd, 2),
            max_drawdown_percent=round(max_dd_pct, 2),
            sharpe_ratio=round(sharpe, 2) if sharpe else None,
            sortino_ratio=round(sortino, 2) if sortino else None,
            calmar_ratio=round(calmar, 2) if calmar else None,
            avg_trade_duration_days=round(avg_duration, 2) if avg_duration else None,
            max_consecutive_wins=max_consec_wins,
            max_consecutive_losses=max_consec_losses,
            expectancy=round(expectancy, 2),
            recovery_factor=round(recovery_factor, 2) if recovery_factor else None,
            ulcer_index=round(ulcer, 2) if ulcer else None
        )

    def _calculate_max_drawdown(
        self,
        equity_curve: List[Dict]
    ) -> tuple[float, float]:
        """
        Рассчитать максимальную просадку

        Args:
            equity_curve: Equity curve

        Returns:
            tuple: (max_drawdown_absolute, max_drawdown_percent)
        """
        if not equity_curve:
            return 0.0, 0.0

        values = [point["total_value"] for point in equity_curve]
        peak = values[0]
        max_dd = 0.0
        max_dd_pct = 0.0

        for value in values:
            if value > peak:
                peak = value

            dd = peak - value
            dd_pct = (dd / peak) * 100 if peak > 0 else 0.0

            if dd > max_dd:
                max_dd = dd
                max_dd_pct = dd_pct

        return max_dd, max_dd_pct

    def _calculate_sharpe_ratio(
        self,
        equity_curve: List[Dict],
        risk_free_rate: float = 0.02
    ) -> Optional[float]:
        """
        Рассчитать Sharpe Ratio

        Args:
            equity_curve: Equity curve
            risk_free_rate: Безрисковая ставка (годовая)

        Returns:
            float | None: Sharpe Ratio
        """
        if len(equity_curve) < 2:
            return None

        # Рассчитать returns
        returns = []
        for i in range(1, len(equity_curve)):
            prev_value = equity_curve[i - 1]["total_value"]
            curr_value = equity_curve[i]["total_value"]

            if prev_value > 0:
                ret = (curr_value - prev_value) / prev_value
                returns.append(ret)

        if not returns:
            return None

        # Среднее и стандартное отклонение
        avg_return = np.mean(returns)
        std_return = np.std(returns)

        if std_return == 0:
            return None

        # Sharpe Ratio (аннуализированный)
        # Предполагаем дневные returns
        periods_per_year = 252  # Торговых дней
        sharpe = (
            (avg_return * periods_per_year - risk_free_rate) /
            (std_return * math.sqrt(periods_per_year))
        )

        return sharpe

    def _calculate_sortino_ratio(
        self,
        equity_curve: List[Dict],
        risk_free_rate: float = 0.02
    ) -> Optional[float]:
        """
        Рассчитать Sortino Ratio

        Отличается от Sharpe тем, что учитывает только downside volatility.

        Args:
            equity_curve: Equity curve
            risk_free_rate: Безрисковая ставка

        Returns:
            float | None: Sortino Ratio
        """
        if len(equity_curve) < 2:
            return None

        returns = []
        for i in range(1, len(equity_curve)):
            prev_value = equity_curve[i - 1]["total_value"]
            curr_value = equity_curve[i]["total_value"]

            if prev_value > 0:
                ret = (curr_value - prev_value) / prev_value
                returns.append(ret)

        if not returns:
            return None

        avg_return = np.mean(returns)

        # Downside deviation (только отрицательные returns)
        downside_returns = [r for r in returns if r < 0]

        if not downside_returns:
            return None

        downside_std = np.std(downside_returns)

        if downside_std == 0:
            return None

        periods_per_year = 252
        sortino = (
            (avg_return * periods_per_year - risk_free_rate) /
            (downside_std * math.sqrt(periods_per_year))
        )

        return sortino

    def _calculate_calmar_ratio(
        self,
        total_return: float,
        max_drawdown_pct: float
    ) -> Optional[float]:
        """
        Рассчитать Calmar Ratio

        Args:
            total_return: Общий return (%)
            max_drawdown_pct: Максимальная просадка (%)

        Returns:
            float | None: Calmar Ratio
        """
        if max_drawdown_pct == 0:
            return None

        return total_return / abs(max_drawdown_pct)

    def _calculate_annualized_return(
        self,
        equity_curve: List[Dict],
        total_return: float
    ) -> Optional[float]:
        """
        Рассчитать аннуализированный return

        Args:
            equity_curve: Equity curve
            total_return: Общий return (%)

        Returns:
            float | None: Аннуализированный return (%)
        """
        if len(equity_curve) < 2:
            return None

        from datetime import datetime

        start_date = datetime.fromisoformat(equity_curve[0]["timestamp"])
        end_date = datetime.fromisoformat(equity_curve[-1]["timestamp"])

        days = (end_date - start_date).days

        if days == 0:
            return None

        years = days / 365.25

        # Аннуализированный return
        annualized = ((1 + total_return / 100) ** (1 / years) - 1) * 100

        return annualized

    def _calculate_consecutive_streaks(
        self,
        trades: List[Trade]
    ) -> tuple[int, int]:
        """
        Рассчитать максимальные серии побед/поражений

        Args:
            trades: Список сделок

        Returns:
            tuple: (max_consecutive_wins, max_consecutive_losses)
        """
        if not trades:
            return 0, 0

        max_wins = 0
        max_losses = 0
        current_wins = 0
        current_losses = 0

        for trade in trades:
            if trade.pnl > 0:
                current_wins += 1
                current_losses = 0
                max_wins = max(max_wins, current_wins)
            elif trade.pnl < 0:
                current_losses += 1
                current_wins = 0
                max_losses = max(max_losses, current_losses)

        return max_wins, max_losses

    def _calculate_avg_trade_duration(
        self,
        trades: List[Trade]
    ) -> Optional[float]:
        """
        Рассчитать среднюю длительность сделки

        Args:
            trades: Список сделок

        Returns:
            float | None: Средняя длительность в днях
        """
        if not trades:
            return None

        durations = []
        for trade in trades:
            duration = (trade.exit_time - trade.entry_time).total_seconds() / 86400
            durations.append(duration)

        return np.mean(durations)

    def _calculate_ulcer_index(
        self,
        equity_curve: List[Dict]
    ) -> Optional[float]:
        """
        Рассчитать Ulcer Index

        Мера downside risk.

        Args:
            equity_curve: Equity curve

        Returns:
            float | None: Ulcer Index
        """
        if len(equity_curve) < 2:
            return None

        values = [point["total_value"] for point in equity_curve]
        drawdowns_squared = []

        peak = values[0]

        for value in values:
            if value > peak:
                peak = value

            dd_pct = ((peak - value) / peak) * 100 if peak > 0 else 0.0
            drawdowns_squared.append(dd_pct ** 2)

        ulcer = math.sqrt(sum(drawdowns_squared) / len(drawdowns_squared))

        return ulcer
