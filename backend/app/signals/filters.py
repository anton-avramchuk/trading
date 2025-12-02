"""
Фильтры для торговых сигналов
"""
from datetime import timedelta
from typing import List, Optional

from loguru import logger

from app.strategies.base import Signal


def filter_by_volume(
    signals: List[Signal],
    min_volume: float,
    volume_data: Optional[dict] = None
) -> List[Signal]:
    """
    Фильтровать сигналы по объёму торгов

    Args:
        signals: Список сигналов
        min_volume: Минимальный объём
        volume_data: Словарь {timestamp: volume} (опционально)

    Returns:
        List[Signal]: Отфильтрованные сигналы
    """
    if not volume_data:
        logger.warning("No volume data provided, skipping volume filter")
        return signals

    filtered = []
    for signal in signals:
        volume = volume_data.get(signal.timestamp, 0)

        if volume >= min_volume:
            filtered.append(signal)
        else:
            logger.debug(
                f"Signal filtered out: volume {volume} < {min_volume} "
                f"at {signal.timestamp}"
            )

    logger.info(
        f"Volume filter: {len(signals)} -> {len(filtered)} signals "
        f"(min volume: {min_volume})"
    )

    return filtered


def filter_by_confidence(
    signals: List[Signal],
    min_confidence: float
) -> List[Signal]:
    """
    Фильтровать сигналы по уверенности (confidence)

    Args:
        signals: Список сигналов
        min_confidence: Минимальная уверенность (0.0 - 1.0)

    Returns:
        List[Signal]: Отфильтрованные сигналы
    """
    filtered = []
    for signal in signals:
        confidence = signal.confidence if signal.confidence is not None else 0.0

        if confidence >= min_confidence:
            filtered.append(signal)
        else:
            logger.debug(
                f"Signal filtered out: confidence {confidence} < {min_confidence} "
                f"at {signal.timestamp}"
            )

    logger.info(
        f"Confidence filter: {len(signals)} -> {len(filtered)} signals "
        f"(min confidence: {min_confidence})"
    )

    return filtered


def filter_duplicates(
    signals: List[Signal],
    time_window: Optional[timedelta] = None
) -> List[Signal]:
    """
    Удалить дубликаты сигналов

    Дубликатом считается сигнал:
    - С тем же типом (BUY/SELL)
    - В пределах time_window от предыдущего сигнала

    Args:
        signals: Список сигналов
        time_window: Временное окно для определения дубликатов
                     (по умолчанию: 1 час)

    Returns:
        List[Signal]: Сигналы без дубликатов
    """
    if time_window is None:
        time_window = timedelta(hours=1)

    if not signals:
        return []

    # Сортировка по времени
    sorted_signals = sorted(signals, key=lambda s: s.timestamp)

    filtered = [sorted_signals[0]]  # Первый сигнал всегда включаем

    for signal in sorted_signals[1:]:
        is_duplicate = False

        # Проверка на дубликат с предыдущими сигналами
        for prev_signal in reversed(filtered):
            # Если разница во времени больше окна, прекратить проверку
            time_diff = signal.timestamp - prev_signal.timestamp
            if time_diff > time_window:
                break

            # Проверка: тот же тип сигнала в пределах окна
            if signal.signal_type == prev_signal.signal_type:
                is_duplicate = True
                logger.debug(
                    f"Duplicate signal: {signal.signal_type} at {signal.timestamp} "
                    f"(previous: {prev_signal.timestamp}, diff: {time_diff})"
                )
                break

        if not is_duplicate:
            filtered.append(signal)

    logger.info(
        f"Duplicate filter: {len(signals)} -> {len(filtered)} signals "
        f"(time window: {time_window})"
    )

    return filtered


def filter_by_signal_type(
    signals: List[Signal],
    signal_types: List[str]
) -> List[Signal]:
    """
    Фильтровать сигналы по типу

    Args:
        signals: Список сигналов
        signal_types: Список допустимых типов ("BUY", "SELL", "HOLD")

    Returns:
        List[Signal]: Отфильтрованные сигналы
    """
    filtered = [s for s in signals if s.signal_type in signal_types]

    logger.info(
        f"Signal type filter: {len(signals)} -> {len(filtered)} signals "
        f"(types: {signal_types})"
    )

    return filtered


def filter_by_price_range(
    signals: List[Signal],
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
) -> List[Signal]:
    """
    Фильтровать сигналы по диапазону цен

    Args:
        signals: Список сигналов
        min_price: Минимальная цена (опционально)
        max_price: Максимальная цена (опционально)

    Returns:
        List[Signal]: Отфильтрованные сигналы
    """
    filtered = []
    for signal in signals:
        if min_price is not None and signal.price < min_price:
            continue
        if max_price is not None and signal.price > max_price:
            continue
        filtered.append(signal)

    logger.info(
        f"Price range filter: {len(signals)} -> {len(filtered)} signals "
        f"(range: {min_price} - {max_price})"
    )

    return filtered


def apply_filters(
    signals: List[Signal],
    min_confidence: Optional[float] = None,
    min_volume: Optional[float] = None,
    volume_data: Optional[dict] = None,
    remove_duplicates: bool = True,
    duplicate_window: Optional[timedelta] = None,
    signal_types: Optional[List[str]] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
) -> List[Signal]:
    """
    Применить несколько фильтров к сигналам

    Args:
        signals: Список сигналов
        min_confidence: Минимальная уверенность
        min_volume: Минимальный объём
        volume_data: Данные объёмов
        remove_duplicates: Удалить дубликаты
        duplicate_window: Временное окно для дубликатов
        signal_types: Допустимые типы сигналов
        min_price: Минимальная цена
        max_price: Максимальная цена

    Returns:
        List[Signal]: Отфильтрованные сигналы
    """
    filtered = signals

    # Фильтр по уверенности
    if min_confidence is not None:
        filtered = filter_by_confidence(filtered, min_confidence)

    # Фильтр по объёму
    if min_volume is not None and volume_data is not None:
        filtered = filter_by_volume(filtered, min_volume, volume_data)

    # Фильтр по типу сигнала
    if signal_types is not None:
        filtered = filter_by_signal_type(filtered, signal_types)

    # Фильтр по диапазону цен
    if min_price is not None or max_price is not None:
        filtered = filter_by_price_range(filtered, min_price, max_price)

    # Удаление дубликатов (последний фильтр)
    if remove_duplicates:
        filtered = filter_duplicates(filtered, duplicate_window)

    logger.info(
        f"Total filtering: {len(signals)} -> {len(filtered)} signals "
        f"({len(signals) - len(filtered)} removed)"
    )

    return filtered
