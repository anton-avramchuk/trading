"""
Базовый класс для всех торговых стратегий
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import pandas as pd
from loguru import logger
from pydantic import BaseModel, Field

from app.indicators import BaseIndicator, IndicatorRegistry


@dataclass
class IndicatorConfig:
    """Конфигурация индикатора для стратегии"""
    name: str  # Название индикатора
    timeframe: str  # Таймфрейм
    parameters: Dict[str, Any]  # Параметры индикатора
    alias: Optional[str] = None  # Алиас для удобства (например, "rsi_1d")


class SignalType:
    """Типы торговых сигналов"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class Signal(BaseModel):
    """Торговый сигнал"""
    signal_type: str = Field(..., description="Тип сигнала: BUY, SELL, HOLD")
    timestamp: pd.Timestamp = Field(..., description="Временная метка")
    price: float = Field(..., description="Цена сигнала")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Уверенность в сигнале")

    # Риск-менеджмент
    stop_loss: Optional[float] = Field(None, description="Уровень Stop Loss")
    take_profit: Optional[float] = Field(None, description="Уровень Take Profit")
    position_size: Optional[float] = Field(None, gt=0.0, description="Размер позиции")

    # Метаданные
    reason: Optional[str] = Field(None, description="Причина генерации сигнала")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Дополнительные данные")

    class Config:
        arbitrary_types_allowed = True


class BaseStrategy(ABC):
    """
    Базовый класс для всех торговых стратегий

    Attributes:
        name: Название стратегии (уникальное)
        description: Описание стратегии
        version: Версия стратегии
        indicators_config: Конфигурация индикаторов
    """

    # Метаданные стратегии (должны быть переопределены в наследниках)
    name: str = "BaseStrategy"
    description: str = "Base strategy class"
    version: str = "1.0.0"

    def __init__(self, **parameters: Any):
        """
        Инициализация стратегии

        Args:
            **parameters: Параметры стратегии
        """
        self.parameters = parameters
        self.indicators_config: List[IndicatorConfig] = []
        self._indicators_cache: Dict[str, BaseIndicator] = {}

        # Инициализация конфигурации индикаторов
        self._setup_indicators()

        logger.debug(f"Initialized strategy: {self.name} v{self.version}")

    @abstractmethod
    def _setup_indicators(self) -> None:
        """
        Настройка индикаторов для стратегии

        Должен заполнить self.indicators_config списком IndicatorConfig
        """
        pass

    @abstractmethod
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
            Signal: Торговый сигнал или None если сигнала нет

        Raises:
            ValueError: Если данные некорректны
        """
        pass

    def add_indicator(
        self,
        name: str,
        timeframe: str,
        parameters: Optional[Dict[str, Any]] = None,
        alias: Optional[str] = None
    ) -> None:
        """
        Добавить индикатор в конфигурацию

        Args:
            name: Название индикатора
            timeframe: Таймфрейм
            parameters: Параметры индикатора
            alias: Алиас индикатора
        """
        config = IndicatorConfig(
            name=name,
            timeframe=timeframe,
            parameters=parameters or {},
            alias=alias
        )
        self.indicators_config.append(config)

        logger.debug(f"Added indicator: {name} on {timeframe}")

    def required_timeframes(self) -> List[str]:
        """
        Получить список необходимых таймфреймов

        Returns:
            List[str]: Список уникальных таймфреймов
        """
        timeframes = {config.timeframe for config in self.indicators_config}
        return sorted(timeframes)

    def calculate_indicators(
        self,
        data: Dict[str, pd.DataFrame]
    ) -> Dict[str, Dict[str, pd.Series]]:
        """
        Рассчитать все индикаторы для стратегии

        Args:
            data: Словарь {timeframe: DataFrame с OHLCV}

        Returns:
            Dict[str, Dict[str, pd.Series]]: Словарь {timeframe: {indicator_alias: Series}}

        Raises:
            ValueError: Если данные для необходимого таймфрейма отсутствуют
        """
        results: Dict[str, Dict[str, pd.Series]] = {}

        for config in self.indicators_config:
            # Проверка наличия данных
            if config.timeframe not in data:
                raise ValueError(
                    f"Missing data for timeframe {config.timeframe} "
                    f"required by indicator {config.name}"
                )

            # Получение или создание индикатора
            indicator = self._get_or_create_indicator(config)

            # Расчёт индикатора
            try:
                result = indicator.calculate(data[config.timeframe])

                # Инициализация словаря для таймфрейма
                if config.timeframe not in results:
                    results[config.timeframe] = {}

                # Сохранение результата
                alias = config.alias or f"{config.name}_{config.timeframe}"

                if isinstance(result, pd.Series):
                    results[config.timeframe][alias] = result
                elif isinstance(result, pd.DataFrame):
                    # Для DataFrame индикаторов (MACD, BBands) сохраняем каждую колонку
                    for col in result.columns:
                        col_alias = f"{alias}_{col}"
                        results[config.timeframe][col_alias] = result[col]

                logger.debug(
                    f"Calculated indicator: {config.name} on {config.timeframe}"
                )

            except Exception as e:
                logger.error(f"Error calculating indicator {config.name}: {e}")
                raise

        return results

    def _get_or_create_indicator(self, config: IndicatorConfig) -> BaseIndicator:
        """
        Получить индикатор из кэша или создать новый

        Args:
            config: Конфигурация индикатора

        Returns:
            BaseIndicator: Экземпляр индикатора
        """
        # Ключ для кэша
        cache_key = f"{config.name}_{config.timeframe}_{hash(str(config.parameters))}"

        if cache_key not in self._indicators_cache:
            # Создание индикатора
            indicator = IndicatorRegistry.create_indicator(
                name=config.name,
                timeframe=config.timeframe,
                **config.parameters
            )
            self._indicators_cache[cache_key] = indicator

        return self._indicators_cache[cache_key]

    def validate_data(self, data: Dict[str, pd.DataFrame]) -> None:
        """
        Валидация входных данных

        Args:
            data: Словарь {timeframe: DataFrame}

        Raises:
            ValueError: Если данные некорректны
        """
        required_tfs = self.required_timeframes()

        for tf in required_tfs:
            if tf not in data:
                raise ValueError(
                    f"Missing required timeframe: {tf}. "
                    f"Required: {required_tfs}"
                )

            if data[tf].empty:
                raise ValueError(f"Empty data for timeframe: {tf}")

            # Проверка обязательных колонок
            required_columns = ["open", "high", "low", "close", "volume"]
            missing = [col for col in required_columns if col not in data[tf].columns]

            if missing:
                raise ValueError(
                    f"Missing columns in {tf} data: {missing}"
                )

    @classmethod
    def get_info(cls) -> Dict[str, Any]:
        """
        Получить информацию о стратегии

        Returns:
            dict: Метаданные стратегии
        """
        return {
            "name": cls.name,
            "description": cls.description,
            "version": cls.version
        }

    def __repr__(self) -> str:
        """Строковое представление стратегии"""
        params_str = ", ".join(f"{k}={v}" for k, v in self.parameters.items())
        return f"{self.name}({params_str})"

    def __str__(self) -> str:
        """Строковое представление стратегии"""
        return self.__repr__()


class StrategyError(Exception):
    """Ошибка при работе со стратегией"""
    pass
