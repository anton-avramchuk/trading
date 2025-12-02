"""
Стратегия на основе RSI (Relative Strength Index)
"""
from typing import Dict, Optional

import pandas as pd

from app.strategies.base import BaseStrategy, Signal, SignalType
from app.strategies.registry import register_strategy


@register_strategy
class RSIStrategy(BaseStrategy):
    """
    Простая стратегия на основе RSI

    Логика:
    - BUY: RSI < oversold_level (перепроданность)
    - SELL: RSI > overbought_level (перекупленность)

    Параметры:
    - rsi_period: Период RSI (по умолчанию 14)
    - oversold_level: Уровень перепроданности (по умолчанию 30)
    - overbought_level: Уровень перекупленности (по умолчанию 70)
    - timeframe: Таймфрейм для анализа (по умолчанию "1d")
    """

    name = "RSIStrategy"
    description = "Торговая стратегия на основе индикатора RSI"
    version = "1.0.0"

    def __init__(
        self,
        rsi_period: int = 14,
        oversold_level: float = 30.0,
        overbought_level: float = 70.0,
        timeframe: str = "1d",
        **kwargs
    ):
        """
        Инициализация стратегии

        Args:
            rsi_period: Период RSI
            oversold_level: Уровень перепроданности
            overbought_level: Уровень перекупленности
            timeframe: Таймфрейм
        """
        self.rsi_period = rsi_period
        self.oversold_level = oversold_level
        self.overbought_level = overbought_level
        self.timeframe = timeframe

        super().__init__(
            rsi_period=rsi_period,
            oversold_level=oversold_level,
            overbought_level=overbought_level,
            timeframe=timeframe,
            **kwargs
        )

    def _setup_indicators(self) -> None:
        """Настройка индикаторов"""
        # Добавляем RSI индикатор
        self.add_indicator(
            name="RSI",
            timeframe=self.timeframe,
            parameters={"period": self.rsi_period},
            alias="rsi"
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

        # Получение RSI
        rsi_values = indicators[self.timeframe]["rsi"]

        # Получение текущего значения RSI
        if current_time not in rsi_values.index:
            return None

        current_rsi = rsi_values.loc[current_time]

        # Проверка на NaN
        if pd.isna(current_rsi):
            return None

        # Получение текущей цены
        current_price = data[self.timeframe].loc[current_time, "close"]

        # Генерация сигнала
        signal_type = None
        confidence = 0.0
        reason = ""

        if current_rsi < self.oversold_level:
            # Перепроданность - сигнал на покупку
            signal_type = SignalType.BUY
            # Чем ниже RSI, тем выше уверенность
            confidence = (self.oversold_level - current_rsi) / self.oversold_level
            reason = f"RSI ({current_rsi:.2f}) below oversold level ({self.oversold_level})"

        elif current_rsi > self.overbought_level:
            # Перекупленность - сигнал на продажу
            signal_type = SignalType.SELL
            # Чем выше RSI, тем выше уверенность
            confidence = (current_rsi - self.overbought_level) / (100 - self.overbought_level)
            reason = f"RSI ({current_rsi:.2f}) above overbought level ({self.overbought_level})"

        # Если нет сигнала
        if signal_type is None:
            return None

        # Расчёт Stop Loss и Take Profit (простая логика)
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
            confidence=min(confidence, 1.0),  # Ограничение [0, 1]
            stop_loss=stop_loss,
            take_profit=take_profit,
            reason=reason,
            metadata={
                "rsi": current_rsi,
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
        # Получение данных до current_time
        historical_data = data.loc[:current_time].tail(period + 1)

        if len(historical_data) < 2:
            # Если недостаточно данных, используем простой range
            return data.loc[current_time, "high"] - data.loc[current_time, "low"]

        # True Range
        prev_close = historical_data["close"].shift(1)
        tr1 = historical_data["high"] - historical_data["low"]
        tr2 = (historical_data["high"] - prev_close).abs()
        tr3 = (historical_data["low"] - prev_close).abs()

        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # ATR как среднее
        atr = true_range.tail(period).mean()

        return atr if not pd.isna(atr) else tr1.iloc[-1]
