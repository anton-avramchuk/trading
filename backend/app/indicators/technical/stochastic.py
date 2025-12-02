"""
Stochastic Oscillator - Стохастический осциллятор
"""
from typing import List

import pandas as pd

from app.indicators.base import BaseIndicator, IndicatorParameter
from app.indicators.registry import register_indicator


@register_indicator
class Stochastic(BaseIndicator):
    """
    Стохастический осциллятор

    Сравнивает текущую цену закрытия с диапазоном цен за период.
    Диапазон: 0-100

    %K = 100 * (Close - Low_N) / (High_N - Low_N)
    %D = SMA(%K, smooth_period)

    - %K > 80: перекупленность
    - %K < 20: перепроданность
    """

    name = "Stochastic"
    category = "momentum"
    description = "Stochastic Oscillator - стохастический осциллятор"

    @classmethod
    def get_parameters_schema(cls) -> List[IndicatorParameter]:
        return [
            IndicatorParameter(
                name="k_period",
                type="int",
                default=14,
                min_value=1,
                max_value=100,
                description="Период для расчёта %K"
            ),
            IndicatorParameter(
                name="d_period",
                type="int",
                default=3,
                min_value=1,
                max_value=50,
                description="Период сглаживания для %D"
            ),
            IndicatorParameter(
                name="smooth_k",
                type="int",
                default=3,
                min_value=1,
                max_value=50,
                description="Период сглаживания %K"
            )
        ]

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Расчёт Stochastic

        Args:
            data: DataFrame с OHLCV данными

        Returns:
            pd.DataFrame: Две колонки - k, d
        """
        self._validate_data(data)

        k_period = self.parameters["k_period"]
        d_period = self.parameters["d_period"]
        smooth_k = self.parameters["smooth_k"]

        # Минимум и максимум за период
        low_min = data["low"].rolling(window=k_period).min()
        high_max = data["high"].rolling(window=k_period).max()

        # %K (Fast)
        k_fast = 100 * (data["close"] - low_min) / (high_max - low_min)

        # %K (Slow) - сглаженный
        k = k_fast.rolling(window=smooth_k).mean()

        # %D - сигнальная линия
        d = k.rolling(window=d_period).mean()

        # Результат
        result = pd.DataFrame({
            "k": k,
            "d": d
        }, index=data.index)

        return result
