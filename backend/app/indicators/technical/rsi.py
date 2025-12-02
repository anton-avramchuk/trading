"""
RSI (Relative Strength Index) - Индекс относительной силы
"""
from typing import List

import pandas as pd

from app.indicators.base import BaseIndicator, IndicatorParameter
from app.indicators.registry import register_indicator


@register_indicator
class RSI(BaseIndicator):
    """
    Индекс относительной силы (RSI)

    RSI измеряет скорость и изменение ценовых движений.
    Диапазон: 0-100
    - RSI > 70: перекупленность
    - RSI < 30: перепроданность
    """

    name = "RSI"
    category = "momentum"
    description = "Relative Strength Index - индекс относительной силы"

    @classmethod
    def get_parameters_schema(cls) -> List[IndicatorParameter]:
        return [
            IndicatorParameter(
                name="period",
                type="int",
                default=14,
                min_value=2,
                max_value=100,
                description="Период RSI"
            ),
            IndicatorParameter(
                name="source",
                type="str",
                default="close",
                description="Источник данных (open, high, low, close)"
            )
        ]

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """
        Расчёт RSI

        Args:
            data: DataFrame с OHLCV данными

        Returns:
            pd.Series: Значения RSI (0-100)
        """
        self._validate_data(data)

        period = self.parameters["period"]
        source = self.parameters["source"]

        if source not in data.columns:
            raise ValueError(f"Invalid source column: {source}")

        # Расчёт изменений цены
        delta = data[source].diff()

        # Разделение на прибыли и убытки
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        # Расчёт средних прибылей и убытков (используем EMA)
        avg_gain = gain.ewm(span=period, adjust=False).mean()
        avg_loss = loss.ewm(span=period, adjust=False).mean()

        # Относительная сила
        rs = avg_gain / avg_loss

        # RSI
        rsi = 100 - (100 / (1 + rs))

        return rsi
