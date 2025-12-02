"""
Multi-Timeframe стратегия - использует несколько таймфреймов
"""
from typing import Dict, Optional

import pandas as pd

from app.strategies.base import BaseStrategy, Signal, SignalType
from app.strategies.registry import register_strategy


@register_strategy
class MultiTimeframeStrategy(BaseStrategy):
    """
    Multi-Timeframe стратегия

    Использует тренд с более высокого таймфрейма для фильтрации сигналов
    на более низком таймфрейме.

    Логика:
    1. Определяем тренд на высоком таймфрейме (например, 1d) через EMA
    2. Генерируем сигналы на низком таймфрейме (например, 1h) через RSI
    3. Фильтруем: покупаем только в восходящем тренде, продаём в нисходящем

    Параметры:
    - high_timeframe: Высокий таймфрейм для определения тренда (по умолчанию "1d")
    - low_timeframe: Низкий таймфрейм для генерации сигналов (по умолчанию "1h")
    - ema_period: Период EMA для тренда (по умолчанию 50)
    - rsi_period: Период RSI для сигналов (по умолчанию 14)
    - oversold: Уровень перепроданности RSI (по умолчанию 30)
    - overbought: Уровень перекупленности RSI (по умолчанию 70)
    """

    name = "MultiTimeframeStrategy"
    description = "Multi-timeframe стратегия с фильтрацией по тренду"
    version = "1.0.0"

    def __init__(
        self,
        high_timeframe: str = "1d",
        low_timeframe: str = "1h",
        ema_period: int = 50,
        rsi_period: int = 14,
        oversold: float = 30.0,
        overbought: float = 70.0,
        **kwargs
    ):
        """
        Инициализация стратегии

        Args:
            high_timeframe: Высокий таймфрейм (тренд)
            low_timeframe: Низкий таймфрейм (сигналы)
            ema_period: Период EMA для тренда
            rsi_period: Период RSI
            oversold: Уровень перепроданности
            overbought: Уровень перекупленности
        """
        self.high_timeframe = high_timeframe
        self.low_timeframe = low_timeframe
        self.ema_period = ema_period
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought

        super().__init__(
            high_timeframe=high_timeframe,
            low_timeframe=low_timeframe,
            ema_period=ema_period,
            rsi_period=rsi_period,
            oversold=oversold,
            overbought=overbought,
            **kwargs
        )

    def _setup_indicators(self) -> None:
        """Настройка индикаторов"""
        # EMA на высоком таймфрейме для определения тренда
        self.add_indicator(
            name="EMA",
            timeframe=self.high_timeframe,
            parameters={"period": self.ema_period},
            alias="ema_high"
        )

        # RSI на низком таймфрейме для генерации сигналов
        self.add_indicator(
            name="RSI",
            timeframe=self.low_timeframe,
            parameters={"period": self.rsi_period},
            alias="rsi_low"
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

        # Получение индикаторов
        ema_high = indicators[self.high_timeframe]["ema_high"]
        rsi_low = indicators[self.low_timeframe]["rsi_low"]

        # Проверка наличия текущего значения
        if current_time not in rsi_low.index:
            return None

        # Определение тренда на высоком таймфрейме
        # Находим ближайшее значение EMA на или до current_time
        ema_mask = ema_high.index <= current_time
        if not ema_mask.any():
            return None

        ema_current = ema_high[ema_mask].iloc[-1]
        high_tf_price = data[self.high_timeframe].loc[
            ema_high[ema_mask].index[-1], "close"
        ]

        # Определение тренда
        is_uptrend = high_tf_price > ema_current
        is_downtrend = high_tf_price < ema_current

        # Получение текущего RSI на низком таймфрейме
        current_rsi = rsi_low.loc[current_time]

        if pd.isna(current_rsi):
            return None

        # Получение текущей цены
        current_price = data[self.low_timeframe].loc[current_time, "close"]

        # Генерация сигнала
        signal_type = None
        confidence = 0.0
        reason = ""

        # BUY: восходящий тренд + перепроданность
        if is_uptrend and current_rsi < self.oversold:
            signal_type = SignalType.BUY
            confidence = (self.oversold - current_rsi) / self.oversold
            reason = (
                f"Uptrend on {self.high_timeframe} + "
                f"RSI oversold ({current_rsi:.2f}) on {self.low_timeframe}"
            )

        # SELL: нисходящий тренд + перекупленность
        elif is_downtrend and current_rsi > self.overbought:
            signal_type = SignalType.SELL
            confidence = (current_rsi - self.overbought) / (100 - self.overbought)
            reason = (
                f"Downtrend on {self.high_timeframe} + "
                f"RSI overbought ({current_rsi:.2f}) on {self.low_timeframe}"
            )

        # Если нет сигнала
        if signal_type is None:
            return None

        # Расчёт Stop Loss и Take Profit
        atr = self._calculate_atr(data[self.low_timeframe], current_time)

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
            confidence=min(confidence, 1.0),
            stop_loss=stop_loss,
            take_profit=take_profit,
            reason=reason,
            metadata={
                "rsi_low": current_rsi,
                "ema_high": ema_current,
                "high_tf_price": high_tf_price,
                "trend": "uptrend" if is_uptrend else "downtrend",
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
