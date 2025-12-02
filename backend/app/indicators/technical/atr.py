"""
ATR (Average True Range) - Средний истинный диапазон
"""
from typing import List

import pandas as pd

from app.indicators.base import BaseIndicator, IndicatorParameter
from app.indicators.registry import register_indicator


@register_indicator
class ATR(BaseIndicator):
    """
    Средний истинный диапазон (ATR)

    Измеряет волатильность рынка.
    True Range = max(high - low, |high - prev_close|, |low - prev_close|)
    ATR = EMA(True Range, period)

    Используется для:
    - Оценки волатильности
    - Установки Stop Loss и Take Profit
    - Определения размера позиции
    """

    name = "ATR"
    category = "volatility"
    description = "Average True Range - средний истинный диапазон"

    @classmethod
    def get_parameters_schema(cls) -> List[IndicatorParameter]:
        return [
            IndicatorParameter(
                name="period",
                type="int",
                default=14,
                min_value=1,
                max_value=100,
                description="Период ATR"
            )
        ]

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """
        Расчёт ATR

        Args:
            data: DataFrame с OHLCV данными

        Returns:
            pd.Series: Значения ATR
        """
        self._validate_data(data)

        period = self.parameters["period"]

        # Предыдущая цена закрытия
        prev_close = data["close"].shift(1)

        # Расчёт True Range
        tr1 = data["high"] - data["low"]
        tr2 = (data["high"] - prev_close).abs()
        tr3 = (data["low"] - prev_close).abs()

        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # ATR = EMA от True Range
        atr = true_range.ewm(span=period, adjust=False).mean()

        return atr
