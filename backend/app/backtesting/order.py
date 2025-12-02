"""
Логика ордеров для бэктестинга
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class OrderType(str, Enum):
    """Тип ордера"""
    MARKET = "MARKET"  # Рыночный ордер
    LIMIT = "LIMIT"    # Лимитный ордер
    STOP = "STOP"      # Стоп-ордер
    STOP_LIMIT = "STOP_LIMIT"  # Стоп-лимит


class OrderSide(str, Enum):
    """Сторона ордера"""
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(str, Enum):
    """Статус ордера"""
    PENDING = "PENDING"      # Ожидает исполнения
    FILLED = "FILLED"        # Исполнен
    PARTIAL = "PARTIAL"      # Частично исполнен
    CANCELLED = "CANCELLED"  # Отменён
    REJECTED = "REJECTED"    # Отклонён


class Order(BaseModel):
    """
    Ордер для бэктестинга

    Поддерживает различные типы ордеров и логику исполнения.
    """
    order_id: str = Field(..., description="Уникальный ID ордера")
    ticker: str = Field(..., description="Тикер инструмента")
    order_type: OrderType = Field(..., description="Тип ордера")
    side: OrderSide = Field(..., description="Сторона (BUY/SELL)")
    quantity: int = Field(..., gt=0, description="Количество")
    price: Optional[float] = Field(None, description="Цена (для лимитных)")
    stop_price: Optional[float] = Field(None, description="Стоп-цена")

    # Метаданные
    created_at: datetime = Field(..., description="Время создания")
    status: OrderStatus = Field(OrderStatus.PENDING, description="Статус ордера")
    filled_quantity: int = Field(0, description="Исполненное количество")
    filled_price: Optional[float] = Field(None, description="Цена исполнения")
    filled_at: Optional[datetime] = Field(None, description="Время исполнения")

    # Stop Loss / Take Profit
    stop_loss: Optional[float] = Field(None, description="Stop Loss цена")
    take_profit: Optional[float] = Field(None, description="Take Profit цена")

    class Config:
        use_enum_values = True

    def can_execute(
        self,
        current_price: float,
        high: Optional[float] = None,
        low: Optional[float] = None
    ) -> bool:
        """
        Проверить, можно ли исполнить ордер при текущей цене

        Args:
            current_price: Текущая цена
            high: Максимальная цена свечи (для стоп-ордеров)
            low: Минимальная цена свечи (для стоп-ордеров)

        Returns:
            bool: True если ордер может быть исполнен
        """
        if self.status not in [OrderStatus.PENDING, OrderStatus.PARTIAL]:
            return False

        if self.order_type == OrderType.MARKET:
            # Рыночный ордер исполняется всегда
            return True

        elif self.order_type == OrderType.LIMIT:
            if self.side == OrderSide.BUY:
                # Лимит на покупку: исполняется когда цена <= limit price
                return current_price <= self.price
            else:
                # Лимит на продажу: исполняется когда цена >= limit price
                return current_price >= self.price

        elif self.order_type == OrderType.STOP:
            if self.stop_price is None:
                return False

            if self.side == OrderSide.BUY:
                # Стоп на покупку: когда цена >= stop price
                if high is not None:
                    return high >= self.stop_price
                return current_price >= self.stop_price
            else:
                # Стоп на продажу: когда цена <= stop price
                if low is not None:
                    return low <= self.stop_price
                return current_price <= self.stop_price

        elif self.order_type == OrderType.STOP_LIMIT:
            # Сначала проверить стоп-условие
            if self.stop_price is None or self.price is None:
                return False

            stop_triggered = False
            if self.side == OrderSide.BUY:
                if high is not None:
                    stop_triggered = high >= self.stop_price
                else:
                    stop_triggered = current_price >= self.stop_price
            else:
                if low is not None:
                    stop_triggered = low <= self.stop_price
                else:
                    stop_triggered = current_price <= self.stop_price

            if not stop_triggered:
                return False

            # После срабатывания стопа проверить лимит
            if self.side == OrderSide.BUY:
                return current_price <= self.price
            else:
                return current_price >= self.price

        return False

    def execute(
        self,
        execution_price: float,
        execution_time: datetime,
        quantity: Optional[int] = None
    ) -> bool:
        """
        Исполнить ордер

        Args:
            execution_price: Цена исполнения
            execution_time: Время исполнения
            quantity: Количество для исполнения (для частичного исполнения)

        Returns:
            bool: True если исполнение успешно
        """
        if self.status not in [OrderStatus.PENDING, OrderStatus.PARTIAL]:
            return False

        exec_quantity = quantity if quantity is not None else self.quantity
        exec_quantity = min(exec_quantity, self.quantity - self.filled_quantity)

        if exec_quantity <= 0:
            return False

        # Обновить параметры исполнения
        self.filled_quantity += exec_quantity
        self.filled_price = execution_price
        self.filled_at = execution_time

        # Обновить статус
        if self.filled_quantity >= self.quantity:
            self.status = OrderStatus.FILLED
        else:
            self.status = OrderStatus.PARTIAL

        return True

    def cancel(self) -> bool:
        """
        Отменить ордер

        Returns:
            bool: True если отмена успешна
        """
        if self.status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED]:
            return False

        self.status = OrderStatus.CANCELLED
        return True

    def get_execution_price(
        self,
        current_price: float,
        high: Optional[float] = None,
        low: Optional[float] = None
    ) -> float:
        """
        Получить цену исполнения

        Args:
            current_price: Текущая цена
            high: Максимальная цена свечи
            low: Минимальная цена свечи

        Returns:
            float: Цена исполнения
        """
        if self.order_type == OrderType.MARKET:
            # Рыночный ордер исполняется по текущей цене
            return current_price

        elif self.order_type == OrderType.LIMIT:
            # Лимитный ордер исполняется по лимит-цене или лучше
            if self.side == OrderSide.BUY:
                # Для покупки: по лимиту или ниже
                return min(self.price, current_price)
            else:
                # Для продажи: по лимиту или выше
                return max(self.price, current_price)

        elif self.order_type == OrderType.STOP:
            # Стоп-ордер превращается в рыночный
            return current_price

        elif self.order_type == OrderType.STOP_LIMIT:
            # Стоп-лимит исполняется по лимит-цене
            if self.side == OrderSide.BUY:
                return min(self.price, current_price)
            else:
                return max(self.price, current_price)

        return current_price

    def is_filled(self) -> bool:
        """Проверить, полностью ли исполнен ордер"""
        return self.status == OrderStatus.FILLED

    def is_active(self) -> bool:
        """Проверить, активен ли ордер"""
        return self.status in [OrderStatus.PENDING, OrderStatus.PARTIAL]

    def remaining_quantity(self) -> int:
        """Получить оставшееся количество"""
        return self.quantity - self.filled_quantity


class OrderManager:
    """
    Менеджер ордеров для бэктестинга

    Управляет активными ордерами и их исполнением.
    """

    def __init__(self):
        self.orders: dict[str, Order] = {}
        self._order_counter = 0

    def create_order(
        self,
        ticker: str,
        order_type: OrderType,
        side: OrderSide,
        quantity: int,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> Order:
        """
        Создать новый ордер

        Args:
            ticker: Тикер
            order_type: Тип ордера
            side: Сторона
            quantity: Количество
            price: Цена (для лимитных)
            stop_price: Стоп-цена
            stop_loss: Stop Loss
            take_profit: Take Profit

        Returns:
            Order: Созданный ордер
        """
        self._order_counter += 1
        order_id = f"ORD{self._order_counter:06d}"

        order = Order(
            order_id=order_id,
            ticker=ticker,
            order_type=order_type,
            side=side,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            created_at=datetime.now(),
            stop_loss=stop_loss,
            take_profit=take_profit
        )

        self.orders[order_id] = order
        return order

    def get_order(self, order_id: str) -> Optional[Order]:
        """Получить ордер по ID"""
        return self.orders.get(order_id)

    def get_active_orders(self, ticker: Optional[str] = None) -> list[Order]:
        """
        Получить активные ордера

        Args:
            ticker: Фильтр по тикеру (опционально)

        Returns:
            List[Order]: Список активных ордеров
        """
        active = [
            order for order in self.orders.values()
            if order.is_active()
        ]

        if ticker:
            active = [order for order in active if order.ticker == ticker]

        return active

    def cancel_order(self, order_id: str) -> bool:
        """Отменить ордер"""
        order = self.orders.get(order_id)
        if order:
            return order.cancel()
        return False

    def cancel_all_orders(self, ticker: Optional[str] = None) -> int:
        """
        Отменить все активные ордера

        Args:
            ticker: Фильтр по тикеру (опционально)

        Returns:
            int: Количество отменённых ордеров
        """
        active_orders = self.get_active_orders(ticker)
        cancelled = 0

        for order in active_orders:
            if order.cancel():
                cancelled += 1

        return cancelled

    def process_orders(
        self,
        ticker: str,
        current_price: float,
        timestamp: datetime,
        high: Optional[float] = None,
        low: Optional[float] = None
    ) -> list[Order]:
        """
        Обработать ордера для заданного тикера и цены

        Args:
            ticker: Тикер
            current_price: Текущая цена
            timestamp: Время
            high: Максимальная цена свечи
            low: Минимальная цена свечи

        Returns:
            List[Order]: Список исполненных ордеров
        """
        active_orders = self.get_active_orders(ticker)
        filled_orders = []

        for order in active_orders:
            if order.can_execute(current_price, high, low):
                execution_price = order.get_execution_price(current_price, high, low)

                if order.execute(execution_price, timestamp):
                    filled_orders.append(order)

        return filled_orders
