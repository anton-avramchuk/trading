"""
Виртуальный портфель для бэктестинга
"""
from datetime import datetime
from typing import Dict, List, Optional

from loguru import logger
from pydantic import BaseModel, Field


class Position(BaseModel):
    """Позиция в портфеле"""
    ticker: str
    quantity: int
    entry_price: float
    entry_time: datetime
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

    def get_value(self, current_price: float) -> float:
        """Получить текущую стоимость позиции"""
        return self.quantity * current_price

    def get_pnl(self, current_price: float) -> float:
        """Получить прибыль/убыток"""
        return (current_price - self.entry_price) * self.quantity

    def get_pnl_percent(self, current_price: float) -> float:
        """Получить прибыль/убыток в процентах"""
        return ((current_price - self.entry_price) / self.entry_price) * 100


class EquityPoint(BaseModel):
    """Точка equity curve"""
    timestamp: datetime
    total_value: float
    cash: float
    positions_value: float
    positions_count: int


class Portfolio:
    """
    Виртуальный портфель для бэктестинга

    Управляет cash, позициями и equity curve.
    """

    def __init__(
        self,
        initial_capital: float = 100000.0,
        commission: float = 0.001,
        slippage: float = 0.0
    ):
        """
        Инициализация портфеля

        Args:
            initial_capital: Начальный капитал
            commission: Комиссия за сделку (% от объёма)
            slippage: Проскальзывание (% от цены)
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.commission = commission
        self.slippage = slippage

        # Позиции: {ticker: Position}
        self.positions: Dict[str, Position] = {}

        # Equity curve
        self.equity_curve: List[EquityPoint] = []

        # История
        self.trade_history: List[Dict] = []

    def buy(
        self,
        ticker: str,
        quantity: int,
        price: float,
        timestamp: datetime,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> bool:
        """
        Купить акции

        Args:
            ticker: Тикер инструмента
            quantity: Количество
            price: Цена покупки
            timestamp: Время сделки
            stop_loss: Stop Loss (опционально)
            take_profit: Take Profit (опционально)

        Returns:
            bool: True если покупка успешна
        """
        # Применить slippage
        execution_price = price * (1 + self.slippage)

        # Рассчитать стоимость
        cost = quantity * execution_price
        commission_cost = cost * self.commission
        total_cost = cost + commission_cost

        # Проверка достаточности средств
        if total_cost > self.cash:
            logger.warning(
                f"Insufficient funds to buy {quantity} {ticker}: "
                f"need {total_cost:.2f}, have {self.cash:.2f}"
            )
            return False

        # Обновить позицию
        if ticker in self.positions:
            # Увеличить существующую позицию
            existing = self.positions[ticker]
            new_quantity = existing.quantity + quantity
            new_avg_price = (
                (existing.entry_price * existing.quantity + execution_price * quantity)
                / new_quantity
            )

            self.positions[ticker] = Position(
                ticker=ticker,
                quantity=new_quantity,
                entry_price=new_avg_price,
                entry_time=existing.entry_time,
                stop_loss=stop_loss or existing.stop_loss,
                take_profit=take_profit or existing.take_profit
            )
        else:
            # Создать новую позицию
            self.positions[ticker] = Position(
                ticker=ticker,
                quantity=quantity,
                entry_price=execution_price,
                entry_time=timestamp,
                stop_loss=stop_loss,
                take_profit=take_profit
            )

        # Списать средства
        self.cash -= total_cost

        # Записать в историю
        self.trade_history.append({
            "timestamp": timestamp,
            "action": "BUY",
            "ticker": ticker,
            "quantity": quantity,
            "price": execution_price,
            "commission": commission_cost,
            "cash_after": self.cash
        })

        logger.info(
            f"BUY {quantity} {ticker} @ {execution_price:.2f} "
            f"(cost: {total_cost:.2f}, cash: {self.cash:.2f})"
        )

        return True

    def sell(
        self,
        ticker: str,
        quantity: int,
        price: float,
        timestamp: datetime
    ) -> bool:
        """
        Продать акции

        Args:
            ticker: Тикер инструмента
            quantity: Количество
            price: Цена продажи
            timestamp: Время сделки

        Returns:
            bool: True если продажа успешна
        """
        # Проверка наличия позиции
        if ticker not in self.positions:
            logger.warning(f"No position to sell for {ticker}")
            return False

        position = self.positions[ticker]

        if position.quantity < quantity:
            logger.warning(
                f"Insufficient position to sell {quantity} {ticker}: "
                f"have {position.quantity}"
            )
            return False

        # Применить slippage
        execution_price = price * (1 - self.slippage)

        # Рассчитать выручку
        proceeds = quantity * execution_price
        commission_cost = proceeds * self.commission
        net_proceeds = proceeds - commission_cost

        # Рассчитать PnL
        pnl = (execution_price - position.entry_price) * quantity

        # Обновить позицию
        if position.quantity == quantity:
            # Полное закрытие позиции
            del self.positions[ticker]
        else:
            # Частичное закрытие
            self.positions[ticker].quantity -= quantity

        # Пополнить cash
        self.cash += net_proceeds

        # Записать в историю
        self.trade_history.append({
            "timestamp": timestamp,
            "action": "SELL",
            "ticker": ticker,
            "quantity": quantity,
            "price": execution_price,
            "commission": commission_cost,
            "pnl": pnl,
            "cash_after": self.cash
        })

        logger.info(
            f"SELL {quantity} {ticker} @ {execution_price:.2f} "
            f"(proceeds: {net_proceeds:.2f}, PnL: {pnl:.2f}, cash: {self.cash:.2f})"
        )

        return True

    def get_position(self, ticker: str) -> Optional[Position]:
        """Получить позицию по тикеру"""
        return self.positions.get(ticker)

    def has_position(self, ticker: str) -> bool:
        """Проверить наличие позиции"""
        return ticker in self.positions

    def get_position_value(
        self,
        ticker: str,
        current_price: float
    ) -> float:
        """Получить текущую стоимость позиции"""
        if ticker not in self.positions:
            return 0.0

        return self.positions[ticker].get_value(current_price)

    def get_total_value(
        self,
        current_prices: Dict[str, float]
    ) -> float:
        """
        Получить общую стоимость портфеля

        Args:
            current_prices: Словарь {ticker: price}

        Returns:
            float: Общая стоимость (cash + позиции)
        """
        positions_value = sum(
            position.get_value(current_prices.get(ticker, position.entry_price))
            for ticker, position in self.positions.items()
        )

        return self.cash + positions_value

    def record_equity(
        self,
        timestamp: datetime,
        current_prices: Dict[str, float]
    ) -> None:
        """
        Записать точку equity curve

        Args:
            timestamp: Время
            current_prices: Текущие цены
        """
        positions_value = sum(
            position.get_value(current_prices.get(ticker, position.entry_price))
            for ticker, position in self.positions.items()
        )

        total_value = self.cash + positions_value

        equity_point = EquityPoint(
            timestamp=timestamp,
            total_value=total_value,
            cash=self.cash,
            positions_value=positions_value,
            positions_count=len(self.positions)
        )

        self.equity_curve.append(equity_point)

    def get_returns(self) -> List[float]:
        """
        Получить список returns (% изменение equity)

        Returns:
            List[float]: Список returns
        """
        if len(self.equity_curve) < 2:
            return []

        returns = []
        for i in range(1, len(self.equity_curve)):
            prev_value = self.equity_curve[i - 1].total_value
            curr_value = self.equity_curve[i].total_value

            if prev_value > 0:
                ret = (curr_value - prev_value) / prev_value
                returns.append(ret)
            else:
                returns.append(0.0)

        return returns

    def get_total_return(self) -> float:
        """
        Получить общий return (%)

        Returns:
            float: Общий return в %
        """
        if not self.equity_curve:
            return 0.0

        final_value = self.equity_curve[-1].total_value
        return ((final_value - self.initial_capital) / self.initial_capital) * 100

    def get_summary(self) -> Dict:
        """
        Получить сводку по портфелю

        Returns:
            dict: Сводная информация
        """
        if not self.equity_curve:
            total_value = self.cash
        else:
            total_value = self.equity_curve[-1].total_value

        return {
            "initial_capital": self.initial_capital,
            "cash": self.cash,
            "positions_count": len(self.positions),
            "total_value": total_value,
            "total_return": self.get_total_return(),
            "trades_count": len(self.trade_history),
            "equity_points": len(self.equity_curve)
        }

    def reset(self) -> None:
        """Сбросить портфель к начальному состоянию"""
        self.cash = self.initial_capital
        self.positions = {}
        self.equity_curve = []
        self.trade_history = []
        logger.info("Portfolio reset to initial state")
