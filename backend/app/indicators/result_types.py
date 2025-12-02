"""
Типы результатов индикаторов
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from pydantic import BaseModel, Field


class ResultType(str, Enum):
    """Типы результатов индикаторов"""
    CONTINUOUS = "continuous"  # Непрерывные значения (MA, RSI)
    DISCRETE = "discrete"      # Дискретные точки (паттерны свечей)
    SHAPE = "shape"           # Геометрические фигуры (зоны, прямоугольники)


class ShapeType(str, Enum):
    """Типы геометрических фигур"""
    RECTANGLE = "rectangle"      # Прямоугольник
    HORIZONTAL_LINE = "hline"   # Горизонтальная линия
    TREND_LINE = "trendline"    # Трендовая линия
    ZONE = "zone"               # Зона (прямоугольник с прозрачностью)


@dataclass
class DiscretePoint:
    """
    Дискретная точка на графике

    Используется для паттернов свечей, разворотных точек, событий
    """
    timestamp: pd.Timestamp
    price: float
    label: str  # Название события (например, "Hammer", "Doji")
    direction: Optional[str] = None  # "UP" или "DOWN" (если применимо)
    metadata: Optional[Dict[str, Any]] = None  # Дополнительные данные

    def to_dict(self) -> Dict[str, Any]:
        """Конвертация в словарь"""
        return {
            "timestamp": str(self.timestamp),
            "price": self.price,
            "label": self.label,
            "direction": self.direction,
            "metadata": self.metadata or {}
        }


@dataclass
class Shape:
    """
    Геометрическая фигура на графике

    Используется для зон поддержки/сопротивления, supply/demand зон, и т.д.
    """
    shape_type: ShapeType
    start_time: pd.Timestamp
    end_time: pd.Timestamp
    price_low: float
    price_high: float
    label: Optional[str] = None  # Название зоны
    color: Optional[str] = None  # Цвет для отображения
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Конвертация в словарь"""
        return {
            "shape_type": self.shape_type.value,
            "start_time": str(self.start_time),
            "end_time": str(self.end_time),
            "price_low": self.price_low,
            "price_high": self.price_high,
            "label": self.label,
            "color": self.color,
            "metadata": self.metadata or {}
        }

    @property
    def width(self) -> pd.Timedelta:
        """Ширина фигуры по времени"""
        return self.end_time - self.start_time

    @property
    def height(self) -> float:
        """Высота фигуры по цене"""
        return self.price_high - self.price_low

    @property
    def center_price(self) -> float:
        """Центральная цена"""
        return (self.price_high + self.price_low) / 2


class IndicatorResult(BaseModel):
    """
    Результат расчёта индикатора

    Универсальный контейнер для всех типов результатов
    """
    result_type: ResultType = Field(..., description="Тип результата")

    # Для CONTINUOUS результатов
    continuous_data: Optional[Union[pd.Series, pd.DataFrame]] = Field(
        None,
        description="Непрерывные данные (Series или DataFrame)"
    )

    # Для DISCRETE результатов
    discrete_points: Optional[List[DiscretePoint]] = Field(
        None,
        description="Список дискретных точек"
    )

    # Для SHAPE результатов
    shapes: Optional[List[Shape]] = Field(
        None,
        description="Список геометрических фигур"
    )

    # Метаданные
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Дополнительные метаданные"
    )

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> Dict[str, Any]:
        """
        Конвертация в словарь для JSON serialization

        Returns:
            dict: Словарь с результатами
        """
        result = {
            "result_type": self.result_type.value,
            "metadata": self.metadata or {}
        }

        if self.result_type == ResultType.CONTINUOUS:
            if self.continuous_data is not None:
                if isinstance(self.continuous_data, pd.Series):
                    result["data"] = {
                        str(timestamp): value
                        for timestamp, value in self.continuous_data.items()
                        if not pd.isna(value)
                    }
                else:  # DataFrame
                    result["data"] = {
                        str(timestamp): row.to_dict()
                        for timestamp, row in self.continuous_data.iterrows()
                    }

        elif self.result_type == ResultType.DISCRETE:
            if self.discrete_points:
                result["points"] = [point.to_dict() for point in self.discrete_points]
            else:
                result["points"] = []

        elif self.result_type == ResultType.SHAPE:
            if self.shapes:
                result["shapes"] = [shape.to_dict() for shape in self.shapes]
            else:
                result["shapes"] = []

        return result

    @classmethod
    def from_continuous(
        cls,
        data: Union[pd.Series, pd.DataFrame],
        metadata: Optional[Dict[str, Any]] = None
    ) -> "IndicatorResult":
        """
        Создать результат из непрерывных данных

        Args:
            data: Series или DataFrame с данными
            metadata: Дополнительные метаданные

        Returns:
            IndicatorResult
        """
        return cls(
            result_type=ResultType.CONTINUOUS,
            continuous_data=data,
            metadata=metadata
        )

    @classmethod
    def from_discrete(
        cls,
        points: List[DiscretePoint],
        metadata: Optional[Dict[str, Any]] = None
    ) -> "IndicatorResult":
        """
        Создать результат из дискретных точек

        Args:
            points: Список DiscretePoint
            metadata: Дополнительные метаданные

        Returns:
            IndicatorResult
        """
        return cls(
            result_type=ResultType.DISCRETE,
            discrete_points=points,
            metadata=metadata
        )

    @classmethod
    def from_shapes(
        cls,
        shapes: List[Shape],
        metadata: Optional[Dict[str, Any]] = None
    ) -> "IndicatorResult":
        """
        Создать результат из геометрических фигур

        Args:
            shapes: Список Shape
            metadata: Дополнительные метаданные

        Returns:
            IndicatorResult
        """
        return cls(
            result_type=ResultType.SHAPE,
            shapes=shapes,
            metadata=metadata
        )
