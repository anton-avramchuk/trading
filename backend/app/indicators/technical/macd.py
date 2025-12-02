"""
MACD (Moving Average Convergence Divergence)
"""
from typing import List

import pandas as pd

from app.indicators.base import BaseIndicator, IndicatorParameter
from app.indicators.registry import register_indicator


@register_indicator
class MACD(BaseIndicator):
    """
    MACD - индикатор схождения-расхождения скользящих средних

    Состоит из трёх линий:
    - MACD Line: быстрая EMA - медленная EMA
    - Signal Line: EMA от MACD Line
    - Histogram: MACD Line - Signal Line

    Используется для определения:
    - Направления тренда
    - Точек разворота
    - Силы тренда
    """

    name = "MACD"
    category = "momentum"
    description = "Moving Average Convergence Divergence - схождение-расхождение скользящих средних"

    @classmethod
    def get_parameters_schema(cls) -> List[IndicatorParameter]:
        return [
            IndicatorParameter(
                name="fast_period",
                type="int",
                default=12,
                min_value=2,
                max_value=100,
                description="Период быстрой EMA"
            ),
            IndicatorParameter(
                name="slow_period",
                type="int",
                default=26,
                min_value=2,
                max_value=200,
                description="Период медленной EMA"
            ),
            IndicatorParameter(
                name="signal_period",
                type="int",
                default=9,
                min_value=2,
                max_value=50,
                description="Период сигнальной линии"
            ),
            IndicatorParameter(
                name="source",
                type="str",
                default="close",
                description="Источник данных (open, high, low, close)"
            )
        ]

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Расчёт MACD

        Args:
            data: DataFrame с OHLCV данными

        Returns:
            pd.DataFrame: Три колонки - macd, signal, histogram
        """
        self._validate_data(data)

        fast_period = self.parameters["fast_period"]
        slow_period = self.parameters["slow_period"]
        signal_period = self.parameters["signal_period"]
        source = self.parameters["source"]

        if source not in data.columns:
            raise ValueError(f"Invalid source column: {source}")

        if fast_period >= slow_period:
            raise ValueError("fast_period must be < slow_period")

        # Расчёт быстрой и медленной EMA
        fast_ema = data[source].ewm(span=fast_period, adjust=False).mean()
        slow_ema = data[source].ewm(span=slow_period, adjust=False).mean()

        # MACD Line
        macd_line = fast_ema - slow_ema

        # Signal Line
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()

        # Histogram
        histogram = macd_line - signal_line

        # Результат
        result = pd.DataFrame({
            "macd": macd_line,
            "signal": signal_line,
            "histogram": histogram
        }, index=data.index)

        return result
