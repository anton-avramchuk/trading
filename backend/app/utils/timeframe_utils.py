"""
Утилиты для работы с таймфреймами
"""
from datetime import timedelta
from typing import Dict, List

from loguru import logger


class TimeframeUtils:
    """Утилиты для работы с таймфреймами"""

    # Маппинг таймфреймов на минуты
    TIMEFRAME_TO_MINUTES: Dict[str, int] = {
        "1m": 1,
        "5m": 5,
        "15m": 15,
        "30m": 30,
        "1h": 60,
        "4h": 240,
        "1d": 1440,
        "1w": 10080,
        "1M": 43200,  # Примерно 30 дней
    }

    # Маппинг таймфреймов на pandas offset
    TIMEFRAME_TO_OFFSET: Dict[str, str] = {
        "1m": "1T",
        "5m": "5T",
        "15m": "15T",
        "30m": "30T",
        "1h": "1H",
        "4h": "4H",
        "1d": "1D",
        "1w": "1W",
        "1M": "1M",
    }

    # Порядок таймфреймов (от меньшего к большему)
    TIMEFRAME_ORDER: List[str] = [
        "1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w", "1M"
    ]

    @classmethod
    def validate_timeframe(cls, timeframe: str) -> bool:
        """
        Проверка корректности таймфрейма

        Args:
            timeframe: Таймфрейм для проверки

        Returns:
            bool: True если таймфрейм корректен
        """
        return timeframe in cls.TIMEFRAME_TO_MINUTES

    @classmethod
    def get_timeframe_minutes(cls, timeframe: str) -> int:
        """
        Получить количество минут для таймфрейма

        Args:
            timeframe: Таймфрейм

        Returns:
            int: Количество минут

        Raises:
            ValueError: Если таймфрейм некорректен
        """
        if not cls.validate_timeframe(timeframe):
            raise ValueError(
                f"Invalid timeframe: {timeframe}. "
                f"Valid: {', '.join(cls.TIMEFRAME_ORDER)}"
            )

        return cls.TIMEFRAME_TO_MINUTES[timeframe]

    @classmethod
    def get_timeframe_offset(cls, timeframe: str) -> str:
        """
        Получить pandas offset для таймфрейма

        Args:
            timeframe: Таймфрейм

        Returns:
            str: Pandas offset (например, "1H", "1D")

        Raises:
            ValueError: Если таймфрейм некорректен
        """
        if not cls.validate_timeframe(timeframe):
            raise ValueError(f"Invalid timeframe: {timeframe}")

        return cls.TIMEFRAME_TO_OFFSET[timeframe]

    @classmethod
    def get_timeframe_timedelta(cls, timeframe: str) -> timedelta:
        """
        Получить timedelta для таймфрейма

        Args:
            timeframe: Таймфрейм

        Returns:
            timedelta: Временной интервал

        Raises:
            ValueError: Если таймфрейм некорректен
        """
        minutes = cls.get_timeframe_minutes(timeframe)
        return timedelta(minutes=minutes)

    @classmethod
    def compare_timeframes(cls, tf1: str, tf2: str) -> int:
        """
        Сравнить два таймфрейма

        Args:
            tf1: Первый таймфрейм
            tf2: Второй таймфрейм

        Returns:
            int: -1 если tf1 < tf2, 0 если равны, 1 если tf1 > tf2

        Raises:
            ValueError: Если таймфреймы некорректны
        """
        minutes1 = cls.get_timeframe_minutes(tf1)
        minutes2 = cls.get_timeframe_minutes(tf2)

        if minutes1 < minutes2:
            return -1
        elif minutes1 > minutes2:
            return 1
        else:
            return 0

    @classmethod
    def is_higher_timeframe(cls, tf1: str, tf2: str) -> bool:
        """
        Проверить, является ли tf1 более высоким таймфреймом чем tf2

        Args:
            tf1: Первый таймфрейм
            tf2: Второй таймфрейм

        Returns:
            bool: True если tf1 > tf2
        """
        return cls.compare_timeframes(tf1, tf2) > 0

    @classmethod
    def get_higher_timeframes(cls, base_timeframe: str) -> List[str]:
        """
        Получить список всех более высоких таймфреймов

        Args:
            base_timeframe: Базовый таймфрейм

        Returns:
            List[str]: Список более высоких таймфреймов

        Raises:
            ValueError: Если таймфрейм некорректен
        """
        if not cls.validate_timeframe(base_timeframe):
            raise ValueError(f"Invalid timeframe: {base_timeframe}")

        base_index = cls.TIMEFRAME_ORDER.index(base_timeframe)
        return cls.TIMEFRAME_ORDER[base_index + 1:]

    @classmethod
    def get_lower_timeframes(cls, base_timeframe: str) -> List[str]:
        """
        Получить список всех более низких таймфреймов

        Args:
            base_timeframe: Базовый таймфрейм

        Returns:
            List[str]: Список более низких таймфреймов

        Raises:
            ValueError: Если таймфрейм некорректен
        """
        if not cls.validate_timeframe(base_timeframe):
            raise ValueError(f"Invalid timeframe: {base_timeframe}")

        base_index = cls.TIMEFRAME_ORDER.index(base_timeframe)
        return cls.TIMEFRAME_ORDER[:base_index]

    @classmethod
    def can_resample(cls, source_tf: str, target_tf: str) -> bool:
        """
        Проверить, можно ли ресемплировать из source_tf в target_tf

        Args:
            source_tf: Исходный таймфрейм
            target_tf: Целевой таймфрейм

        Returns:
            bool: True если ресемплинг возможен (source < target)
        """
        try:
            return cls.is_higher_timeframe(target_tf, source_tf)
        except ValueError:
            return False

    @classmethod
    def get_multiplier(cls, source_tf: str, target_tf: str) -> int:
        """
        Получить множитель для конвертации между таймфреймами

        Args:
            source_tf: Исходный таймфрейм
            target_tf: Целевой таймфрейм

        Returns:
            int: Множитель (сколько свечей source_tf в одной свече target_tf)

        Raises:
            ValueError: Если ресемплинг невозможен
        """
        if not cls.can_resample(source_tf, target_tf):
            raise ValueError(
                f"Cannot resample from {source_tf} to {target_tf}. "
                f"Source must be lower than target."
            )

        source_minutes = cls.get_timeframe_minutes(source_tf)
        target_minutes = cls.get_timeframe_minutes(target_tf)

        if target_minutes % source_minutes != 0:
            logger.warning(
                f"Target timeframe {target_tf} is not a clean multiple of {source_tf}. "
                f"Multiplier: {target_minutes / source_minutes}"
            )

        return target_minutes // source_minutes

    @classmethod
    def get_all_timeframes(cls) -> List[str]:
        """
        Получить список всех поддерживаемых таймфреймов

        Returns:
            List[str]: Список таймфреймов
        """
        return cls.TIMEFRAME_ORDER.copy()

    @classmethod
    def sort_timeframes(cls, timeframes: List[str], reverse: bool = False) -> List[str]:
        """
        Отсортировать таймфреймы

        Args:
            timeframes: Список таймфреймов
            reverse: Обратный порядок (от большего к меньшему)

        Returns:
            List[str]: Отсортированный список

        Raises:
            ValueError: Если есть некорректные таймфреймы
        """
        # Проверка всех таймфреймов
        for tf in timeframes:
            if not cls.validate_timeframe(tf):
                raise ValueError(f"Invalid timeframe: {tf}")

        # Сортировка по индексу в TIMEFRAME_ORDER
        sorted_tfs = sorted(
            timeframes,
            key=lambda tf: cls.TIMEFRAME_ORDER.index(tf),
            reverse=reverse
        )

        return sorted_tfs
