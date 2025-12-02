"""
Менеджер управления рисками для торговых сигналов
"""
from datetime import datetime
from typing import List, Optional

import pandas as pd
from loguru import logger

from app.strategies.base import Signal


class RiskManager:
    """
    Менеджер рисков для торговых сигналов

    Применяет правила риск-менеджмента:
    - Расчёт размера позиции
    - Установка Stop Loss / Take Profit на основе ATR
    - Фильтрация по лимитам (количество сигналов, размер позиции)
    """

    def __init__(
        self,
        max_position_size: float = 0.1,
        max_daily_signals: int = 5,
        atr_period: int = 14,
        atr_multiplier_sl: float = 2.0,
        atr_multiplier_tp: float = 3.0,
        risk_reward_ratio: float = 1.5,
        portfolio_value: float = 100000.0,
        risk_per_trade: float = 0.02
    ):
        """
        Инициализация менеджера рисков

        Args:
            max_position_size: Максимальный размер позиции (% от портфеля)
            max_daily_signals: Максимальное количество сигналов в день
            atr_period: Период для расчёта ATR
            atr_multiplier_sl: Множитель ATR для Stop Loss
            atr_multiplier_tp: Множитель ATR для Take Profit
            risk_reward_ratio: Соотношение Risk/Reward (если не используется ATR)
            portfolio_value: Размер портфеля для расчёта размера позиции
            risk_per_trade: Риск на сделку (% от портфеля)
        """
        self.max_position_size = max_position_size
        self.max_daily_signals = max_daily_signals
        self.atr_period = atr_period
        self.atr_multiplier_sl = atr_multiplier_sl
        self.atr_multiplier_tp = atr_multiplier_tp
        self.risk_reward_ratio = risk_reward_ratio
        self.portfolio_value = portfolio_value
        self.risk_per_trade = risk_per_trade

    def apply_risk_management(
        self,
        signal: Signal,
        data: pd.DataFrame
    ) -> Signal:
        """
        Применить риск-менеджмент к сигналу

        Рассчитывает и устанавливает:
        - Stop Loss
        - Take Profit
        - Position Size

        Args:
            signal: Исходный сигнал
            data: Исторические OHLCV данные

        Returns:
            Signal: Обновлённый сигнал с риск-параметрами
        """
        try:
            # Рассчитать ATR
            atr = self._calculate_atr(data)

            if atr is None or pd.isna(atr):
                logger.warning("Cannot calculate ATR, using default risk parameters")
                atr = signal.price * 0.02  # 2% от цены как fallback

            # Установить Stop Loss (если не установлен)
            if signal.stop_loss is None:
                signal.stop_loss = self.calculate_stop_loss(signal, atr)

            # Установить Take Profit (если не установлен)
            if signal.take_profit is None:
                signal.take_profit = self.calculate_take_profit(signal, atr)

            # Установить Position Size (если не установлен)
            if signal.position_size is None:
                signal.position_size = self.calculate_position_size(signal)

            return signal

        except Exception as e:
            logger.error(f"Error applying risk management: {e}")
            return signal

    def calculate_position_size(
        self,
        signal: Signal,
        portfolio_value: Optional[float] = None
    ) -> float:
        """
        Рассчитать размер позиции на основе риска

        Args:
            signal: Торговый сигнал
            portfolio_value: Размер портфеля (опционально)

        Returns:
            float: Размер позиции в %
        """
        if portfolio_value is None:
            portfolio_value = self.portfolio_value

        # Если есть stop loss, рассчитать на основе риска
        if signal.stop_loss:
            risk_per_share = abs(signal.price - signal.stop_loss)
            max_loss = portfolio_value * self.risk_per_trade

            if risk_per_share > 0:
                shares = max_loss / risk_per_share
                position_value = shares * signal.price
                position_size = position_value / portfolio_value

                # Ограничить максимальным размером
                position_size = min(position_size, self.max_position_size)
            else:
                position_size = self.max_position_size
        else:
            # Без stop loss используем максимальный размер
            position_size = self.max_position_size

        return round(position_size, 4)

    def calculate_stop_loss(
        self,
        signal: Signal,
        atr: float
    ) -> float:
        """
        Рассчитать Stop Loss на основе ATR

        Args:
            signal: Торговый сигнал
            atr: Значение ATR

        Returns:
            float: Цена Stop Loss
        """
        if signal.signal_type == "BUY":
            # Для покупки: SL ниже цены входа
            stop_loss = signal.price - (atr * self.atr_multiplier_sl)
        elif signal.signal_type == "SELL":
            # Для продажи: SL выше цены входа
            stop_loss = signal.price + (atr * self.atr_multiplier_sl)
        else:
            stop_loss = signal.price

        return round(stop_loss, 2)

    def calculate_take_profit(
        self,
        signal: Signal,
        atr: Optional[float] = None
    ) -> float:
        """
        Рассчитать Take Profit

        Args:
            signal: Торговый сигнал
            atr: Значение ATR (опционально)

        Returns:
            float: Цена Take Profit
        """
        if atr is not None:
            # Использовать ATR
            if signal.signal_type == "BUY":
                take_profit = signal.price + (atr * self.atr_multiplier_tp)
            elif signal.signal_type == "SELL":
                take_profit = signal.price - (atr * self.atr_multiplier_tp)
            else:
                take_profit = signal.price
        else:
            # Использовать Risk/Reward ratio
            if signal.stop_loss:
                risk = abs(signal.price - signal.stop_loss)
                reward = risk * self.risk_reward_ratio

                if signal.signal_type == "BUY":
                    take_profit = signal.price + reward
                elif signal.signal_type == "SELL":
                    take_profit = signal.price - reward
                else:
                    take_profit = signal.price
            else:
                # Fallback: 3% от цены
                if signal.signal_type == "BUY":
                    take_profit = signal.price * 1.03
                elif signal.signal_type == "SELL":
                    take_profit = signal.price * 0.97
                else:
                    take_profit = signal.price

        return round(take_profit, 2)

    def filter_signals(
        self,
        signals: List[Signal],
        max_daily_signals: Optional[int] = None
    ) -> List[Signal]:
        """
        Фильтровать сигналы по дневному лимиту

        Args:
            signals: Список сигналов
            max_daily_signals: Максимум сигналов в день (опционально)

        Returns:
            List[Signal]: Отфильтрованные сигналы
        """
        if max_daily_signals is None:
            max_daily_signals = self.max_daily_signals

        # Группировка по дате
        signals_by_date = {}
        for signal in signals:
            date_key = signal.timestamp.date()
            if date_key not in signals_by_date:
                signals_by_date[date_key] = []
            signals_by_date[date_key].append(signal)

        # Фильтрация: оставить топ N сигналов по confidence для каждого дня
        filtered_signals = []
        for date_key, day_signals in signals_by_date.items():
            # Сортировка по confidence (убывание)
            sorted_signals = sorted(
                day_signals,
                key=lambda s: s.confidence if s.confidence else 0.0,
                reverse=True
            )

            # Взять топ N
            top_signals = sorted_signals[:max_daily_signals]
            filtered_signals.extend(top_signals)

        logger.info(
            f"Filtered signals: {len(signals)} -> {len(filtered_signals)} "
            f"(max {max_daily_signals} per day)"
        )

        return filtered_signals

    def _calculate_atr(self, data: pd.DataFrame) -> Optional[float]:
        """
        Рассчитать ATR (Average True Range)

        Args:
            data: OHLCV данные

        Returns:
            float | None: Значение ATR или None
        """
        if len(data) < self.atr_period:
            return None

        try:
            # Расчёт True Range
            high_low = data["high"] - data["low"]
            high_close = abs(data["high"] - data["close"].shift())
            low_close = abs(data["low"] - data["close"].shift())

            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

            # ATR как EMA true range
            atr = true_range.ewm(span=self.atr_period, adjust=False).mean()

            return atr.iloc[-1]

        except Exception as e:
            logger.error(f"Error calculating ATR: {e}")
            return None

    def validate_signal(self, signal: Signal) -> bool:
        """
        Валидация сигнала

        Проверяет корректность параметров риск-менеджмента.

        Args:
            signal: Торговый сигнал

        Returns:
            bool: True если сигнал валиден
        """
        # Проверка Stop Loss
        if signal.stop_loss:
            if signal.signal_type == "BUY" and signal.stop_loss >= signal.price:
                logger.warning(
                    f"Invalid BUY signal: SL ({signal.stop_loss}) >= "
                    f"Price ({signal.price})"
                )
                return False

            if signal.signal_type == "SELL" and signal.stop_loss <= signal.price:
                logger.warning(
                    f"Invalid SELL signal: SL ({signal.stop_loss}) <= "
                    f"Price ({signal.price})"
                )
                return False

        # Проверка Take Profit
        if signal.take_profit:
            if signal.signal_type == "BUY" and signal.take_profit <= signal.price:
                logger.warning(
                    f"Invalid BUY signal: TP ({signal.take_profit}) <= "
                    f"Price ({signal.price})"
                )
                return False

            if signal.signal_type == "SELL" and signal.take_profit >= signal.price:
                logger.warning(
                    f"Invalid SELL signal: TP ({signal.take_profit}) >= "
                    f"Price ({signal.price})"
                )
                return False

        # Проверка Position Size
        if signal.position_size:
            if signal.position_size <= 0 or signal.position_size > self.max_position_size:
                logger.warning(
                    f"Invalid position size: {signal.position_size} "
                    f"(max: {self.max_position_size})"
                )
                return False

        return True
