"""
Генератор торговых сигналов
"""
from datetime import date, datetime
from typing import Dict, List, Optional

import pandas as pd
from loguru import logger
from sqlalchemy.orm import Session

from app.core.data_manager import DataManager
from app.models.signal import Signal as SignalModel
from app.strategies.base import BaseStrategy, Signal


class SignalGenerator:
    """
    Генератор торговых сигналов на основе стратегии

    Принимает стратегию и генерирует сигналы на исторических данных.
    Поддерживает multi-timeframe стратегии.
    """

    def __init__(
        self,
        strategy: BaseStrategy,
        risk_manager: Optional["RiskManager"] = None,
        db_session: Optional[Session] = None,
        warm_up_bars: int = 100
    ):
        """
        Инициализация генератора

        Args:
            strategy: Стратегия для генерации сигналов
            risk_manager: Менеджер рисков (опционально)
            db_session: Сессия БД для сохранения сигналов
            warm_up_bars: Минимальное количество баров для расчёта индикаторов
        """
        self.strategy = strategy
        self.risk_manager = risk_manager
        self.db_session = db_session
        self.warm_up_bars = warm_up_bars

        # Статистика
        self.stats = {
            "total_points": 0,
            "signals_generated": 0,
            "buy_signals": 0,
            "sell_signals": 0,
            "signals_saved": 0
        }

    def generate_signals(
        self,
        ticker: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Signal]:
        """
        Генерация сигналов на исторических данных

        Args:
            ticker: Тикер инструмента
            start_date: Начальная дата (опционально)
            end_date: Конечная дата (опционально)

        Returns:
            List[Signal]: Список сгенерированных сигналов
        """
        logger.info(
            f"Generating signals for {ticker} using strategy '{self.strategy.name}'"
        )

        # Сброс статистики
        self.stats = {
            "total_points": 0,
            "signals_generated": 0,
            "buy_signals": 0,
            "sell_signals": 0,
            "signals_saved": 0
        }

        # Загрузка multi-timeframe данных
        timeframes = self.strategy.required_timeframes()
        logger.info(f"Loading data for timeframes: {timeframes}")

        data_manager = DataManager()
        try:
            multi_tf_data = data_manager.get_multi_timeframe_data(
                ticker=ticker,
                timeframes=timeframes,
                start_date=start_date,
                end_date=end_date
            )
        except Exception as e:
            logger.error(f"Failed to load data for {ticker}: {e}")
            return []

        if not multi_tf_data:
            logger.warning(f"No data found for {ticker}")
            return []

        # Определить базовый таймфрейм (самый низкий)
        base_timeframe = min(
            timeframes,
            key=lambda tf: data_manager._get_timeframe_minutes(tf)
        )
        base_data = multi_tf_data[base_timeframe]

        logger.info(
            f"Base timeframe: {base_timeframe}, "
            f"total bars: {len(base_data)}, "
            f"warm-up bars: {self.warm_up_bars}"
        )

        if len(base_data) < self.warm_up_bars:
            logger.warning(
                f"Not enough data for warm-up period "
                f"({len(base_data)} < {self.warm_up_bars})"
            )
            return []

        # Генерация сигналов для каждой точки
        signals: List[Signal] = []

        for i in range(self.warm_up_bars, len(base_data)):
            current_time = base_data.index[i]
            self.stats["total_points"] += 1

            # Создать срез данных до текущей точки (избегаем look-ahead bias)
            data_slice = self._get_data_slice(multi_tf_data, i, base_timeframe)

            # Генерация сигнала
            try:
                signal = self.generate_signal_for_point(data_slice, current_time)

                if signal:
                    # Применить риск-менеджер
                    if self.risk_manager:
                        signal = self.risk_manager.apply_risk_management(
                            signal,
                            data_slice[base_timeframe]
                        )

                    signals.append(signal)
                    self.stats["signals_generated"] += 1

                    if signal.signal_type == "BUY":
                        self.stats["buy_signals"] += 1
                    elif signal.signal_type == "SELL":
                        self.stats["sell_signals"] += 1

            except Exception as e:
                logger.error(
                    f"Error generating signal at {current_time} "
                    f"for {ticker}: {e}"
                )
                continue

            # Логирование прогресса каждые 10%
            if self.stats["total_points"] % max(1, (len(base_data) - self.warm_up_bars) // 10) == 0:
                progress = (i - self.warm_up_bars) / (len(base_data) - self.warm_up_bars) * 100
                logger.info(
                    f"Progress: {progress:.1f}%, "
                    f"signals: {self.stats['signals_generated']}"
                )

        # Сохранение сигналов в БД
        if self.db_session and signals:
            self._save_signals_to_db(ticker, signals)

        logger.info(
            f"Signal generation completed: {self.stats['signals_generated']} signals "
            f"({self.stats['buy_signals']} BUY, {self.stats['sell_signals']} SELL) "
            f"from {self.stats['total_points']} points"
        )

        return signals

    def generate_signal_for_point(
        self,
        data: Dict[str, pd.DataFrame],
        current_time: pd.Timestamp
    ) -> Optional[Signal]:
        """
        Генерация сигнала для конкретной точки

        Args:
            data: Словарь с multi-timeframe данными (срез до current_time)
            current_time: Текущее время

        Returns:
            Signal | None: Сгенерированный сигнал или None
        """
        try:
            # Вызвать стратегию
            signal = self.strategy.generate_signal(data, current_time)

            if signal:
                # Добавить timestamp, если не установлен
                if not signal.timestamp:
                    signal.timestamp = current_time

            return signal

        except Exception as e:
            logger.error(f"Error in strategy '{self.strategy.name}': {e}")
            return None

    def _get_data_slice(
        self,
        multi_tf_data: Dict[str, pd.DataFrame],
        end_idx: int,
        base_timeframe: str
    ) -> Dict[str, pd.DataFrame]:
        """
        Получить срез данных до определённого индекса

        Создаёт срез для всех таймфреймов, учитывая соответствие времени.

        Args:
            multi_tf_data: Полные multi-timeframe данные
            end_idx: Индекс конечной точки в базовом таймфрейме
            base_timeframe: Базовый таймфрейм

        Returns:
            Dict[str, pd.DataFrame]: Срез данных для каждого таймфрейма
        """
        base_data = multi_tf_data[base_timeframe]
        current_time = base_data.index[end_idx]

        data_slice = {}

        for timeframe, df in multi_tf_data.items():
            # Взять все данные до current_time включительно
            slice_df = df[df.index <= current_time].copy()
            data_slice[timeframe] = slice_df

        return data_slice

    def _save_signals_to_db(self, ticker: str, signals: List[Signal]) -> None:
        """
        Сохранение сигналов в БД

        Args:
            ticker: Тикер инструмента
            signals: Список сигналов для сохранения
        """
        if not self.db_session:
            logger.warning("No DB session provided, signals not saved")
            return

        try:
            # Получить instrument_id
            from app.models.instrument import Instrument

            instrument = (
                self.db_session.query(Instrument)
                .filter(Instrument.ticker == ticker)
                .first()
            )

            if not instrument:
                logger.error(f"Instrument {ticker} not found in database")
                return

            # Создать SignalModel объекты
            for signal in signals:
                signal_model = SignalModel(
                    instrument_id=instrument.id,
                    strategy_name=self.strategy.name,
                    signal_type=signal.signal_type,
                    timestamp=signal.timestamp,
                    price=signal.price,
                    confidence=signal.confidence,
                    position_size=signal.position_size,
                    stop_loss=signal.stop_loss,
                    take_profit=signal.take_profit
                )
                self.db_session.add(signal_model)

            self.db_session.commit()
            self.stats["signals_saved"] = len(signals)
            logger.info(f"Saved {len(signals)} signals to database")

        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to save signals to database: {e}")

    def get_stats(self) -> Dict:
        """
        Получить статистику генерации

        Returns:
            dict: Статистика
        """
        return self.stats.copy()
