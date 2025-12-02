"""
Стратегия на основе MACD (Moving Average Convergence Divergence)
"""
from typing import Dict, Optional

import pandas as pd

from app.strategies.base import BaseStrategy, Signal, SignalType
from app.strategies.registry import register_strategy


@register_strategy
class MACDStrategy(BaseStrategy):
    """
    Стратегия на основе MACD

    Логика:
    - BUY: MACD пересекает сигнальную линию снизу вверх (bullish crossover)
    - SELL: MACD пересекает сигнальную линию сверху вниз (bearish crossover)

    Дополнительная фильтрация по histogram:
    - BUY: histogram > 0 (подтверждение бычьего тренда)
    - SELL: histogram < 0 (подтверждение медвежьего тренда)

    Параметры:
    - fast_period: Период быстрой EMA (по умолчанию 12)
    - slow_period: Период медленной EMA (по умолчанию 26)
    - signal_period: Период сигнальной линии (по умолчанию 9)
    - timeframe: Таймфрейм для анализа (по умолчанию "1d")
    """

    name = "MACDStrategy"
    description = "Торговая стратегия на основе индикатора MACD"
    version = "1.0.0"

    def __init__(
        self,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
        timeframe: str = "1d",
        **kwargs
    ):
        """
        Инициализация стратегии

        Args:
            fast_period: Период быстрой EMA
            slow_period: Период медленной EMA
            signal_period: Период сигнальной линии
            timeframe: Таймфрейм
        """
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        self.timeframe = timeframe

        super().__init__(
            fast_period=fast_period,
            slow_period=slow_period,
            signal_period=signal_period,
            timeframe=timeframe,
            **kwargs
        )

    def _setup_indicators(self) -> None:
        """Настройка индикаторов"""
        # Добавляем MACD индикатор
        self.add_indicator(
            name="MACD",
            timeframe=self.timeframe,
            parameters={
                "fast_period": self.fast_period,
                "slow_period": self.slow_period,
                "signal_period": self.signal_period
            },
            alias="macd"
        )

    def generate_signal(
        self,
        data: Dict[str, pd.DataFrame],
        current_time: pd.Timestamp
    ) -> Optional[Signal]:
        """
        Генерация торгового сигнала

        Args:
            data: Словарь {timeframe: DataFrame с OHLCV}
            current_time: Текущая временная метка

        Returns:
            Signal: Торговый сигнал или None
        """
        # Валидация данных
        self.validate_data(data)

        # Расчёт индикаторов
        indicators = self.calculate_indicators(data)

        # Получение MACD компонентов
        macd_line = indicators[self.timeframe]["macd_macd"]
        signal_line = indicators[self.timeframe]["macd_signal"]
        histogram = indicators[self.timeframe]["macd_histogram"]

        # Проверка наличия текущего значения
        if current_time not in macd_line.index:
            return None

        # Получение текущих и предыдущих значений
        current_idx = macd_line.index.get_loc(current_time)

        if current_idx == 0:
            # Нет предыдущего значения
            return None

        prev_time = macd_line.index[current_idx - 1]

        current_macd = macd_line.loc[current_time]
        current_signal = signal_line.loc[current_time]
        current_histogram = histogram.loc[current_time]

        prev_macd = macd_line.loc[prev_time]
        prev_signal = signal_line.loc[prev_time]

        # Проверка на NaN
        if any(pd.isna(val) for val in [
            current_macd, current_signal, current_histogram,
            prev_macd, prev_signal
        ]):
            return None

        # Получение текущей цены
        current_price = data[self.timeframe].loc[current_time, "close"]

        # Определение пересечений
        signal_type = None
        confidence = 0.0
        reason = ""

        # Bullish crossover: MACD пересекает signal снизу вверх
        if prev_macd <= prev_signal and current_macd > current_signal:
            signal_type = SignalType.BUY
            # Уверенность зависит от размера histogram
            confidence = min(abs(current_histogram) / 0.5, 1.0)
            reason = f"MACD bullish crossover (histogram: {current_histogram:.4f})"

        # Bearish crossover: MACD пересекает signal сверху вниз
        elif prev_macd >= prev_signal and current_macd < current_signal:
            signal_type = SignalType.SELL
            # Уверенность зависит от размера histogram
            confidence = min(abs(current_histogram) / 0.5, 1.0)
            reason = f"MACD bearish crossover (histogram: {current_histogram:.4f})"

        # Если нет сигнала
        if signal_type is None:
            return None

        # Расчёт Stop Loss и Take Profit
        atr = self._calculate_atr(data[self.timeframe], current_time)

        if signal_type == SignalType.BUY:
            stop_loss = current_price - (2 * atr)
            take_profit = current_price + (3 * atr)
        else:  # SELL
            stop_loss = current_price + (2 * atr)
            take_profit = current_price - (3 * atr)

        return Signal(
            signal_type=signal_type,
            timestamp=current_time,
            price=current_price,
            confidence=confidence,
            stop_loss=stop_loss,
            take_profit=take_profit,
            reason=reason,
            metadata={
                "macd": current_macd,
                "signal": current_signal,
                "histogram": current_histogram,
                "atr": atr
            }
        )

    def _calculate_atr(
        self,
        data: pd.DataFrame,
        current_time: pd.Timestamp,
        period: int = 14
    ) -> float:
        """
        Простой расчёт ATR для установки Stop Loss / Take Profit

        Args:
            data: DataFrame с OHLCV
            current_time: Текущее время
            period: Период ATR

        Returns:
            float: Значение ATR
        """
        historical_data = data.loc[:current_time].tail(period + 1)

        if len(historical_data) < 2:
            return data.loc[current_time, "high"] - data.loc[current_time, "low"]

        prev_close = historical_data["close"].shift(1)
        tr1 = historical_data["high"] - historical_data["low"]
        tr2 = (historical_data["high"] - prev_close).abs()
        tr3 = (historical_data["low"] - prev_close).abs()

        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.tail(period).mean()

        return atr if not pd.isna(atr) else tr1.iloc[-1]
