"""
Индикатор уровней Pivot Points
"""
from typing import List

import pandas as pd

from app.indicators.base import BaseIndicator, IndicatorParameter
from app.indicators.registry import register_indicator
from app.indicators.result_types import IndicatorResult, Shape, ShapeType


@register_indicator
class PivotPoints(BaseIndicator):
    """
    Индикатор уровней Pivot Points

    Рассчитывает уровни поддержки и сопротивления на основе
    предыдущего периода (день, неделя, месяц).

    Формулы для стандартных пивотов:
    - PP (Pivot Point) = (High + Low + Close) / 3
    - R1 = 2*PP - Low
    - R2 = PP + (High - Low)
    - R3 = High + 2*(PP - Low)
    - S1 = 2*PP - High
    - S2 = PP - (High - Low)
    - S3 = Low - 2*(High - PP)

    Возвращает горизонтальные линии для каждого уровня.
    """

    name = "PivotPoints"
    category = "custom"
    description = "Уровни поддержки/сопротивления на основе предыдущего периода"

    def __init__(
        self,
        timeframe: str = "1d",
        **parameters
    ):
        super().__init__(timeframe=timeframe, **parameters)

    @classmethod
    def get_parameters_schema(cls) -> List[IndicatorParameter]:
        """Схема параметров индикатора"""
        return [
            IndicatorParameter(
                name="period",
                type="str",
                default="daily",
                description="Период для расчёта пивотов (daily, weekly, monthly)"
            ),
            IndicatorParameter(
                name="pivot_type",
                type="str",
                default="standard",
                description="Тип пивотов (standard, fibonacci, camarilla)"
            ),
            IndicatorParameter(
                name="show_mid_levels",
                type="int",
                default=0,
                min_value=0,
                max_value=1,
                description="Показывать промежуточные уровни (M1-M5)"
            )
        ]

    def calculate(self, data: pd.DataFrame) -> IndicatorResult:
        """
        Расчёт уровней Pivot Points

        Args:
            data: DataFrame с OHLCV данными

        Returns:
            IndicatorResult с горизонтальными линиями
        """
        self._validate_data(data)

        if len(data) < 2:
            return IndicatorResult.from_shapes(
                shapes=[],
                metadata={"levels_found": 0}
            )

        # Параметры
        period = self.parameters["period"]
        pivot_type = self.parameters["pivot_type"]
        show_mid_levels = bool(self.parameters["show_mid_levels"])

        # Определить период для группировки
        if period == "daily":
            freq = "D"
        elif period == "weekly":
            freq = "W"
        elif period == "monthly":
            freq = "M"
        else:
            freq = "D"

        df = data.copy()

        # Группировка по периодам
        df["period"] = df.index.to_period(freq)

        # Расчёт пивотов для каждого периода
        pivot_levels: List[Shape] = []

        periods = df["period"].unique()

        for i in range(1, len(periods)):
            prev_period = periods[i-1]
            current_period = periods[i]

            # Данные предыдущего периода
            prev_data = df[df["period"] == prev_period]

            if len(prev_data) == 0:
                continue

            high = prev_data["high"].max()
            low = prev_data["low"].min()
            close = prev_data["close"].iloc[-1]

            # Данные текущего периода для определения времени отображения
            current_data = df[df["period"] == current_period]

            if len(current_data) == 0:
                continue

            start_time = current_data.index[0]
            end_time = current_data.index[-1]

            # Расчёт уровней в зависимости от типа
            if pivot_type == "standard":
                levels = self._calculate_standard_pivots(high, low, close)
            elif pivot_type == "fibonacci":
                levels = self._calculate_fibonacci_pivots(high, low, close)
            elif pivot_type == "camarilla":
                levels = self._calculate_camarilla_pivots(high, low, close)
            else:
                levels = self._calculate_standard_pivots(high, low, close)

            # Создать горизонтальные линии для каждого уровня
            for level_name, level_price in levels.items():
                # Определить цвет и тип
                if level_name == "PP":
                    color = "#2196F3"  # Синий
                    level_type = "pivot"
                elif level_name.startswith("R"):
                    color = "#F44336"  # Красный
                    level_type = "resistance"
                elif level_name.startswith("S"):
                    color = "#4CAF50"  # Зеленый
                    level_type = "support"
                elif level_name.startswith("M"):
                    if not show_mid_levels:
                        continue
                    color = "#9E9E9E"  # Серый
                    level_type = "midpoint"
                else:
                    color = "#9E9E9E"
                    level_type = "other"

                pivot_levels.append(Shape(
                    shape_type=ShapeType.HORIZONTAL_LINE,
                    start_time=start_time,
                    end_time=end_time,
                    price_low=level_price,
                    price_high=level_price,
                    label=f"{level_name} ({level_price:.2f})",
                    color=color,
                    metadata={
                        "level_type": level_type,
                        "level_name": level_name,
                        "price": level_price,
                        "period": str(current_period),
                        "pivot_type": pivot_type
                    }
                ))

        return IndicatorResult.from_shapes(
            shapes=pivot_levels,
            metadata={
                "levels_found": len(pivot_levels),
                "period": period,
                "pivot_type": pivot_type,
                "timeframe": self.timeframe
            }
        )

    def _calculate_standard_pivots(
        self,
        high: float,
        low: float,
        close: float
    ) -> dict:
        """
        Расчёт стандартных пивотов

        Args:
            high: Максимум предыдущего периода
            low: Минимум предыдущего периода
            close: Закрытие предыдущего периода

        Returns:
            dict: Словарь уровней {название: цена}
        """
        pp = (high + low + close) / 3

        r1 = 2 * pp - low
        r2 = pp + (high - low)
        r3 = high + 2 * (pp - low)

        s1 = 2 * pp - high
        s2 = pp - (high - low)
        s3 = low - 2 * (high - pp)

        levels = {
            "PP": pp,
            "R1": r1,
            "R2": r2,
            "R3": r3,
            "S1": s1,
            "S2": s2,
            "S3": s3
        }

        # Промежуточные уровни
        levels["M1"] = (pp + r1) / 2
        levels["M2"] = (r1 + r2) / 2
        levels["M3"] = (r2 + r3) / 2
        levels["M4"] = (pp + s1) / 2
        levels["M5"] = (s1 + s2) / 2

        return levels

    def _calculate_fibonacci_pivots(
        self,
        high: float,
        low: float,
        close: float
    ) -> dict:
        """
        Расчёт Fibonacci пивотов

        Args:
            high: Максимум предыдущего периода
            low: Минимум предыдущего периода
            close: Закрытие предыдущего периода

        Returns:
            dict: Словарь уровней
        """
        pp = (high + low + close) / 3
        range_hl = high - low

        r1 = pp + 0.382 * range_hl
        r2 = pp + 0.618 * range_hl
        r3 = pp + 1.000 * range_hl

        s1 = pp - 0.382 * range_hl
        s2 = pp - 0.618 * range_hl
        s3 = pp - 1.000 * range_hl

        return {
            "PP": pp,
            "R1": r1,
            "R2": r2,
            "R3": r3,
            "S1": s1,
            "S2": s2,
            "S3": s3
        }

    def _calculate_camarilla_pivots(
        self,
        high: float,
        low: float,
        close: float
    ) -> dict:
        """
        Расчёт Camarilla пивотов

        Args:
            high: Максимум предыдущего периода
            low: Минимум предыдущего периода
            close: Закрытие предыдущего периода

        Returns:
            dict: Словарь уровней
        """
        range_hl = high - low

        r4 = close + range_hl * 1.1 / 2
        r3 = close + range_hl * 1.1 / 4
        r2 = close + range_hl * 1.1 / 6
        r1 = close + range_hl * 1.1 / 12

        s1 = close - range_hl * 1.1 / 12
        s2 = close - range_hl * 1.1 / 6
        s3 = close - range_hl * 1.1 / 4
        s4 = close - range_hl * 1.1 / 2

        return {
            "R1": r1,
            "R2": r2,
            "R3": r3,
            "R4": r4,
            "S1": s1,
            "S2": s2,
            "S3": s3,
            "S4": s4
        }
