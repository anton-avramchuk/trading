"""
Индикатор паттернов свечей
"""
from typing import List

import pandas as pd

from app.indicators.base import BaseIndicator, IndicatorParameter
from app.indicators.registry import register_indicator
from app.indicators.result_types import DiscretePoint, IndicatorResult


@register_indicator
class CandlePatterns(BaseIndicator):
    """
    Индикатор для распознавания паттернов японских свечей

    Определяет следующие паттерны:
    - Hammer (Молот) - бычий разворот
    - Inverted Hammer (Перевёрнутый молот) - бычий разворот
    - Hanging Man (Повешенный) - медвежий разворот
    - Shooting Star (Падающая звезда) - медвежий разворот
    - Doji (Доджи) - нерешительность
    - Bullish Engulfing (Бычье поглощение)
    - Bearish Engulfing (Медвежье поглощение)

    Возвращает дискретные точки для каждого обнаруженного паттерна.
    """

    name = "CandlePatterns"
    category = "custom"
    description = "Распознавание паттернов японских свечей"

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
                name="doji_threshold",
                type="float",
                default=0.1,
                min_value=0.0,
                max_value=0.5,
                description="Порог для определения Doji (% от диапазона)"
            ),
            IndicatorParameter(
                name="shadow_ratio",
                type="float",
                default=2.0,
                min_value=1.5,
                max_value=5.0,
                description="Минимальное соотношение тени к телу для Hammer/Shooting Star"
            ),
            IndicatorParameter(
                name="min_body_size",
                type="float",
                default=0.001,
                min_value=0.0,
                max_value=0.1,
                description="Минимальный размер тела свечи (% от цены)"
            )
        ]

    def calculate(self, data: pd.DataFrame) -> IndicatorResult:
        """
        Расчёт паттернов свечей

        Args:
            data: DataFrame с OHLCV данными

        Returns:
            IndicatorResult с дискретными точками
        """
        self._validate_data(data)

        if len(data) < 2:
            return IndicatorResult.from_discrete(
                points=[],
                metadata={"patterns_found": 0}
            )

        # Параметры
        doji_threshold = self.parameters["doji_threshold"]
        shadow_ratio = self.parameters["shadow_ratio"]
        min_body_size = self.parameters["min_body_size"]

        # Расчёт характеристик свечей
        df = data.copy()
        df["body"] = abs(df["close"] - df["open"])
        df["range"] = df["high"] - df["low"]
        df["upper_shadow"] = df["high"] - df[["open", "close"]].max(axis=1)
        df["lower_shadow"] = df[["open", "close"]].min(axis=1) - df["low"]
        df["body_pct"] = df["body"] / df["close"]

        # Направление свечи
        df["direction"] = df.apply(
            lambda row: "UP" if row["close"] > row["open"] else "DOWN",
            axis=1
        )

        patterns: List[DiscretePoint] = []

        # Проход по свечам
        for i in range(1, len(df)):
            idx = df.index[i]
            row = df.iloc[i]
            prev_row = df.iloc[i-1]

            # Doji - тело очень маленькое относительно диапазона
            if row["range"] > 0 and row["body"] / row["range"] < doji_threshold:
                patterns.append(DiscretePoint(
                    timestamp=idx,
                    price=row["close"],
                    label="Doji",
                    direction=None,
                    metadata={
                        "body_ratio": round(row["body"] / row["range"], 4),
                        "strength": "high" if row["body"] / row["range"] < doji_threshold / 2 else "medium"
                    }
                ))

            # Пропускаем паттерны с очень маленьким телом
            if row["body_pct"] < min_body_size:
                continue

            # Hammer - длинная нижняя тень, маленькое тело вверху, бычий разворот
            if (row["lower_shadow"] > row["body"] * shadow_ratio and
                row["upper_shadow"] < row["body"] * 0.5 and
                row["direction"] == "UP" and
                prev_row["direction"] == "DOWN"):

                patterns.append(DiscretePoint(
                    timestamp=idx,
                    price=row["close"],
                    label="Hammer",
                    direction="UP",
                    metadata={
                        "shadow_to_body": round(row["lower_shadow"] / row["body"], 2),
                        "strength": "high" if row["lower_shadow"] > row["body"] * shadow_ratio * 1.5 else "medium"
                    }
                ))

            # Inverted Hammer - длинная верхняя тень, маленькое тело внизу
            if (row["upper_shadow"] > row["body"] * shadow_ratio and
                row["lower_shadow"] < row["body"] * 0.5 and
                row["direction"] == "UP" and
                prev_row["direction"] == "DOWN"):

                patterns.append(DiscretePoint(
                    timestamp=idx,
                    price=row["close"],
                    label="Inverted Hammer",
                    direction="UP",
                    metadata={
                        "shadow_to_body": round(row["upper_shadow"] / row["body"], 2),
                        "strength": "medium"
                    }
                ))

            # Hanging Man - длинная нижняя тень после восходящего тренда
            if (row["lower_shadow"] > row["body"] * shadow_ratio and
                row["upper_shadow"] < row["body"] * 0.5 and
                row["direction"] == "DOWN" and
                prev_row["direction"] == "UP"):

                patterns.append(DiscretePoint(
                    timestamp=idx,
                    price=row["close"],
                    label="Hanging Man",
                    direction="DOWN",
                    metadata={
                        "shadow_to_body": round(row["lower_shadow"] / row["body"], 2),
                        "strength": "high" if row["lower_shadow"] > row["body"] * shadow_ratio * 1.5 else "medium"
                    }
                ))

            # Shooting Star - длинная верхняя тень после восходящего тренда
            if (row["upper_shadow"] > row["body"] * shadow_ratio and
                row["lower_shadow"] < row["body"] * 0.5 and
                row["direction"] == "DOWN" and
                prev_row["direction"] == "UP"):

                patterns.append(DiscretePoint(
                    timestamp=idx,
                    price=row["close"],
                    label="Shooting Star",
                    direction="DOWN",
                    metadata={
                        "shadow_to_body": round(row["upper_shadow"] / row["body"], 2),
                        "strength": "high" if row["upper_shadow"] > row["body"] * shadow_ratio * 1.5 else "medium"
                    }
                ))

            # Bullish Engulfing - текущая зелёная свеча полностью поглощает предыдущую красную
            if (row["direction"] == "UP" and
                prev_row["direction"] == "DOWN" and
                row["open"] < prev_row["close"] and
                row["close"] > prev_row["open"] and
                row["body"] > prev_row["body"]):

                patterns.append(DiscretePoint(
                    timestamp=idx,
                    price=row["close"],
                    label="Bullish Engulfing",
                    direction="UP",
                    metadata={
                        "body_ratio": round(row["body"] / prev_row["body"], 2),
                        "strength": "high" if row["body"] > prev_row["body"] * 1.5 else "medium"
                    }
                ))

            # Bearish Engulfing - текущая красная свеча полностью поглощает предыдущую зелёную
            if (row["direction"] == "DOWN" and
                prev_row["direction"] == "UP" and
                row["open"] > prev_row["close"] and
                row["close"] < prev_row["open"] and
                row["body"] > prev_row["body"]):

                patterns.append(DiscretePoint(
                    timestamp=idx,
                    price=row["close"],
                    label="Bearish Engulfing",
                    direction="DOWN",
                    metadata={
                        "body_ratio": round(row["body"] / prev_row["body"], 2),
                        "strength": "high" if row["body"] > prev_row["body"] * 1.5 else "medium"
                    }
                ))

        return IndicatorResult.from_discrete(
            points=patterns,
            metadata={
                "patterns_found": len(patterns),
                "timeframe": self.timeframe,
                "data_points": len(data)
            }
        )
