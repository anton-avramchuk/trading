# Архитектура сервиса торговых сигналов

## Обзор системы

Система предназначена для анализа исторических данных российского фондового рынка и товарных фьючерсов с возможностью генерации торговых сигналов и бэктестинга стратегий.

### Ключевые возможности
- Анализ исторических данных по множественным таймфреймам
- Расширяемая система кастомных индикаторов
- Индикаторы из разных таймфреймов в одной стратегии
- Связывание тикеров с индексами
- Генерация торговых сигналов с учётом риск-менеджмента
- Бэктестинг стратегий
- Веб-интерфейс для визуализации
- Миграция с CSV на базу данных

---

## Технологический стек

### Backend
- **Python 3.11+**
- **FastAPI** - REST API и веб-сервер
- **Pandas / Polars** - обработка временных рядов
- **NumPy** - математические вычисления
- **TA-Lib / Pandas-TA** - технические индикаторы
- **SQLAlchemy** - ORM для работы с БД
- **Alembic** - миграции БД
- **Pydantic** - валидация данных

### Database
- **PostgreSQL** - основная БД (TimescaleDB расширение для временных рядов)
- **Redis** (опционально) - кэш для индикаторов

### Frontend
- **Angular 17+** - фреймворк (standalone компоненты)
- **TypeScript**
- **RxJS** - реактивное программирование
- **Apache ECharts** (через **ngx-echarts**) - графики
- **Angular Material** или **PrimeNG** - UI компоненты
- **NgRx** (опционально) - state management
- **Angular Signals** - новый реактивный API

---

## Структура проекта

```
trading-signals/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # Точка входа FastAPI
│   │   ├── config.py                  # Конфигурация
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── data_loader.py         # Загрузка из CSV/БД
│   │   │   ├── data_manager.py        # Управление данными
│   │   │   ├── timeframe_manager.py   # Работа с таймфреймами
│   │   │   └── cache.py               # Кэширование расчётов
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── database.py            # Настройка БД
│   │   │   ├── instrument.py          # Модель инструмента (тикер)
│   │   │   ├── index.py               # Модель индекса
│   │   │   ├── ohlcv.py               # Модель свечей
│   │   │   ├── signal.py              # Модель сигнала
│   │   │   └── strategy.py            # Модель стратегии
│   │   │
│   │   ├── indicators/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # Базовый класс индикатора
│   │   │   ├── registry.py            # Реестр индикаторов
│   │   │   ├── technical/             # Технические индикаторы
│   │   │   │   ├── __init__.py
│   │   │   │   ├── moving_average.py  # MA, EMA, SMA
│   │   │   │   ├── momentum.py        # RSI, Stochastic
│   │   │   │   ├── trend.py           # MACD, ADX
│   │   │   │   └── volatility.py      # Bollinger, ATR
│   │   │   └── custom/                # Кастомные индикаторы
│   │   │       ├── __init__.py
│   │   │       └── example.py
│   │   │
│   │   ├── signals/
│   │   │   ├── __init__.py
│   │   │   ├── generator.py           # Генератор сигналов
│   │   │   ├── risk_manager.py        # Риск-менеджмент
│   │   │   └── filters.py             # Фильтры сигналов
│   │   │
│   │   ├── backtesting/
│   │   │   ├── __init__.py
│   │   │   ├── engine.py              # Движок бэктестинга
│   │   │   ├── portfolio.py           # Виртуальный портфель
│   │   │   ├── order.py               # Логика ордеров
│   │   │   └── reporter.py            # Отчёты о бэктесте
│   │   │
│   │   ├── strategies/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # Базовый класс стратегии
│   │   │   ├── registry.py            # Реестр стратегий
│   │   │   └── examples/
│   │   │       ├── ma_cross.py        # Пример: пересечение MA
│   │   │       └── rsi_oversold.py    # Пример: RSI перепроданность
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── instruments.py     # Эндпоинты инструментов
│   │   │   │   ├── data.py            # Эндпоинты данных
│   │   │   │   ├── indicators.py      # Эндпоинты индикаторов
│   │   │   │   ├── signals.py         # Эндпоинты сигналов
│   │   │   │   ├── backtesting.py     # Эндпоинты бэктеста
│   │   │   │   └── strategies.py      # Эндпоинты стратегий
│   │   │   └── deps.py                # Зависимости
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── instrument.py          # Pydantic схемы
│   │   │   ├── signal.py
│   │   │   ├── indicator.py
│   │   │   └── backtest.py
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── csv_importer.py        # Импорт CSV
│   │       ├── data_validator.py      # Валидация данных
│   │       └── helpers.py             # Вспомогательные функции
│   │
│   ├── migrations/                     # Alembic миграции
│   │   └── versions/
│   │
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── fixtures/
│   │
│   ├── requirements.txt
│   └── pyproject.toml
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── app.component.ts
│   │   │   ├── app.component.html
│   │   │   ├── app.component.scss
│   │   │   ├── app.config.ts
│   │   │   ├── app.routes.ts
│   │   │   │
│   │   │   ├── core/
│   │   │   │   ├── services/
│   │   │   │   │   ├── api.service.ts         # HTTP клиент
│   │   │   │   │   ├── websocket.service.ts   # WebSocket
│   │   │   │   │   ├── auth.service.ts        # Аутентификация
│   │   │   │   │   └── storage.service.ts     # LocalStorage
│   │   │   │   ├── interceptors/
│   │   │   │   │   ├── auth.interceptor.ts
│   │   │   │   │   └── error.interceptor.ts
│   │   │   │   └── guards/
│   │   │   │       └── auth.guard.ts
│   │   │   │
│   │   │   ├── shared/
│   │   │   │   ├── components/
│   │   │   │   │   ├── loader/
│   │   │   │   │   ├── error-message/
│   │   │   │   │   └── confirm-dialog/
│   │   │   │   ├── directives/
│   │   │   │   ├── pipes/
│   │   │   │   │   ├── date-format.pipe.ts
│   │   │   │   │   └── number-format.pipe.ts
│   │   │   │   └── models/
│   │   │   │       ├── instrument.model.ts
│   │   │   │       ├── indicator.model.ts
│   │   │   │       ├── signal.model.ts
│   │   │   │       └── backtest.model.ts
│   │   │   │
│   │   │   ├── features/
│   │   │   │   ├── dashboard/
│   │   │   │   │   ├── dashboard.component.ts
│   │   │   │   │   ├── dashboard.component.html
│   │   │   │   │   ├── dashboard.component.scss
│   │   │   │   │   └── dashboard.routes.ts
│   │   │   │   │
│   │   │   │   ├── analysis/
│   │   │   │   │   ├── analysis.component.ts
│   │   │   │   │   ├── components/
│   │   │   │   │   │   ├── chart/
│   │   │   │   │   │   │   ├── candlestick-chart.component.ts
│   │   │   │   │   │   │   ├── indicator-overlay.component.ts
│   │   │   │   │   │   │   └── signal-markers.component.ts
│   │   │   │   │   │   ├── instrument-selector/
│   │   │   │   │   │   │   └── instrument-selector.component.ts
│   │   │   │   │   │   └── indicator-panel/
│   │   │   │   │   │       ├── indicator-panel.component.ts
│   │   │   │   │   │       └── indicator-config.component.ts
│   │   │   │   │   ├── services/
│   │   │   │   │   │   └── analysis.service.ts
│   │   │   │   │   └── analysis.routes.ts
│   │   │   │   │
│   │   │   │   ├── signals/
│   │   │   │   │   ├── signals.component.ts
│   │   │   │   │   ├── components/
│   │   │   │   │   │   ├── signal-list/
│   │   │   │   │   │   ├── signal-details/
│   │   │   │   │   │   └── signal-filters/
│   │   │   │   │   ├── services/
│   │   │   │   │   │   └── signals.service.ts
│   │   │   │   │   └── signals.routes.ts
│   │   │   │   │
│   │   │   │   ├── strategies/
│   │   │   │   │   ├── strategies.component.ts
│   │   │   │   │   ├── components/
│   │   │   │   │   │   ├── strategy-list/
│   │   │   │   │   │   ├── strategy-builder/
│   │   │   │   │   │   └── strategy-details/
│   │   │   │   │   ├── services/
│   │   │   │   │   │   └── strategies.service.ts
│   │   │   │   │   └── strategies.routes.ts
│   │   │   │   │
│   │   │   │   ├── backtesting/
│   │   │   │   │   ├── backtesting.component.ts
│   │   │   │   │   ├── components/
│   │   │   │   │   │   ├── backtest-config/
│   │   │   │   │   │   ├── backtest-results/
│   │   │   │   │   │   ├── trade-list/
│   │   │   │   │   │   └── equity-curve/
│   │   │   │   │   ├── services/
│   │   │   │   │   │   └── backtesting.service.ts
│   │   │   │   │   └── backtesting.routes.ts
│   │   │   │   │
│   │   │   │   └── instruments/
│   │   │   │       ├── instruments.component.ts
│   │   │   │       ├── components/
│   │   │   │       │   ├── instrument-list/
│   │   │   │       │   └── instrument-form/
│   │   │   │       ├── services/
│   │   │   │       │   └── instruments.service.ts
│   │   │   │       └── instruments.routes.ts
│   │   │   │
│   │   │   └── store/                         # NgRx (опционально)
│   │   │       ├── actions/
│   │   │       ├── reducers/
│   │   │       ├── effects/
│   │   │       └── selectors/
│   │   │
│   │   ├── main.ts
│   │   ├── index.html
│   │   └── styles.scss
│   │
│   ├── angular.json
│   ├── package.json
│   ├── tsconfig.json
│   └── tsconfig.app.json
│
├── data/                               # Директория для CSV файлов
│   ├── moex/                           # Московская биржа
│   ├── futures/                        # Фьючерсы
│   └── indexes/                        # Индексы
│
├── docker-compose.yml
├── .env.example
└── README.md
```

### Angular Configuration

#### package.json
```json
{
  "name": "trading-signals-frontend",
  "version": "1.0.0",
  "scripts": {
    "ng": "ng",
    "start": "ng serve",
    "build": "ng build",
    "watch": "ng build --watch --configuration development",
    "test": "ng test"
  },
  "dependencies": {
    "@angular/animations": "^17.0.0",
    "@angular/common": "^17.0.0",
    "@angular/compiler": "^17.0.0",
    "@angular/core": "^17.0.0",
    "@angular/forms": "^17.0.0",
    "@angular/platform-browser": "^17.0.0",
    "@angular/platform-browser-dynamic": "^17.0.0",
    "@angular/router": "^17.0.0",
    "@ngrx/store": "^17.0.0",
    "@ngrx/effects": "^17.0.0",
    "echarts": "^5.4.3",
    "ngx-echarts": "^17.0.0",
    "rxjs": "^7.8.1",
    "tslib": "^2.6.2",
    "zone.js": "^0.14.2"
  },
  "devDependencies": {
    "@angular-devkit/build-angular": "^17.0.0",
    "@angular/cli": "^17.0.0",
    "@angular/compiler-cli": "^17.0.0",
    "typescript": "~5.2.2"
  }
}
```

#### tsconfig.json
```json
{
  "compileOnSave": false,
  "compilerOptions": {
    "outDir": "./dist/out-tsc",
    "forceConsistentCasingInFileNames": true,
    "strict": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "esModuleInterop": true,
    "sourceMap": true,
    "declaration": false,
    "experimentalDecorators": true,
    "moduleResolution": "node",
    "importHelpers": true,
    "target": "ES2022",
    "module": "ES2022",
    "useDefineForClassFields": false,
    "lib": [
      "ES2022",
      "dom"
    ]
  },
  "angularCompilerOptions": {
    "enableI18nLegacyMessageIdFormat": false,
    "strictInjectionParameters": true,
    "strictInputAccessModifiers": true,
    "strictTemplates": true
  }
}
```

---

## Архитектура модулей

### 1. Data Management Layer

**Ответственность:** Загрузка, хранение и предоставление доступа к данным

#### Ключевые компоненты:

**DataLoader** - загрузка данных из источников
```python
class DataLoader:
    def load_from_csv(ticker: str, timeframe: str, path: str) -> pd.DataFrame
    def load_from_db(ticker: str, timeframe: str, start: date, end: date) -> pd.DataFrame
    def migrate_csv_to_db(csv_path: str, ticker: str) -> None
```

**DataManager** - управление данными
```python
class DataManager:
    def get_data(ticker: str, timeframe: str, start: date, end: date) -> pd.DataFrame
    def save_data(ticker: str, timeframe: str, data: pd.DataFrame) -> None
    def resample_timeframe(data: pd.DataFrame, target_tf: str) -> pd.DataFrame
```

**TimeframeManager** - работа с множественными таймфреймами
```python
class TimeframeManager:
    def align_timeframes(data_dict: dict[str, pd.DataFrame]) -> dict
    def get_higher_timeframe_value(data: pd.DataFrame, current_time: datetime, tf: str) -> float
```

---

### 2. Indicator Engine

**Ответственность:** Расчёт технических индикаторов

#### Базовая структура:

```python
class BaseIndicator(ABC):
    name: str
    parameters: dict
    timeframe: str  # Таймфрейм индикатора
    
    @abstractmethod
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        pass
    
    def validate_parameters(self) -> bool:
        pass
```

**IndicatorRegistry** - реестр всех индикаторов
```python
class IndicatorRegistry:
    def register(indicator_class: Type[BaseIndicator]) -> None
    def get_indicator(name: str) -> Type[BaseIndicator]
    def list_available() -> list[str]
    def get_by_category(category: str) -> list[Type[BaseIndicator]]
```

#### Пример индикатора:
```python
@register_indicator
class MovingAverage(BaseIndicator):
    name = "MA"
    
    def __init__(self, period: int = 20, ma_type: str = "SMA", timeframe: str = "1d"):
        self.period = period
        self.ma_type = ma_type
        self.timeframe = timeframe
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        if self.ma_type == "SMA":
            return data['close'].rolling(window=self.period).mean()
        elif self.ma_type == "EMA":
            return data['close'].ewm(span=self.period).mean()
```

---

### 3. Signal Generation

**Ответственность:** Генерация торговых сигналов на основе индикаторов

```python
class SignalGenerator:
    def __init__(self, strategy: Strategy):
        self.strategy = strategy
        self.risk_manager = RiskManager()
    
    def generate_signals(self, data: dict[str, pd.DataFrame]) -> list[Signal]:
        """
        data: словарь {timeframe: DataFrame}
        Возвращает список сигналов
        """
        pass
    
    def apply_risk_management(self, signals: list[Signal]) -> list[Signal]:
        return self.risk_manager.filter_signals(signals)
```

**RiskManager** - управление рисками
```python
class RiskManager:
    def __init__(self, max_position_size: float = 0.1, max_daily_signals: int = 5):
        self.max_position_size = max_position_size
        self.max_daily_signals = max_daily_signals
    
    def filter_signals(self, signals: list[Signal]) -> list[Signal]:
        # Фильтрация по размеру позиции, количеству сигналов и т.д.
        pass
    
    def calculate_position_size(self, signal: Signal, portfolio_value: float) -> float:
        pass
```

---

### 4. Strategy System

**Ответственность:** Определение торговых стратегий

```python
class BaseStrategy(ABC):
    name: str
    indicators: list[BaseIndicator]
    
    @abstractmethod
    def generate_signal(self, data: dict[str, pd.DataFrame]) -> Signal | None:
        """
        data содержит данные по всем необходимым таймфреймам
        """
        pass
    
    def add_indicator(self, indicator: BaseIndicator, timeframe: str) -> None:
        pass
```

**StrategyRegistry** - управление стратегиями
```python
class StrategyRegistry:
    def register(strategy_class: Type[BaseStrategy]) -> None
    def get_strategy(name: str) -> Type[BaseStrategy]
    def list_strategies() -> list[str]
```

#### Пример стратегии с multi-timeframe:
```python
@register_strategy
class TrendFollowing(BaseStrategy):
    name = "Trend Following Multi-TF"
    
    def __init__(self):
        # MA на дневном таймфрейме для тренда
        self.ma_daily = MovingAverage(period=50, timeframe="1d")
        # RSI на часовом для входа
        self.rsi_hourly = RSI(period=14, timeframe="1h")
        
    def generate_signal(self, data: dict[str, pd.DataFrame]) -> Signal | None:
        daily_data = data["1d"]
        hourly_data = data["1h"]
        
        ma_daily = self.ma_daily.calculate(daily_data)
        rsi_hourly = self.rsi_hourly.calculate(hourly_data)
        
        # Логика: восходящий тренд на дневках + перепроданность на часовках
        if daily_data['close'].iloc[-1] > ma_daily.iloc[-1] and rsi_hourly.iloc[-1] < 30:
            return Signal(type="BUY", price=hourly_data['close'].iloc[-1])
        
        return None
```

---

### 5. Backtesting Engine

**Ответственность:** Тестирование стратегий на исторических данных

```python
class BacktestEngine:
    def __init__(self, strategy: BaseStrategy, initial_capital: float = 100000):
        self.strategy = strategy
        self.portfolio = Portfolio(initial_capital)
        self.trades = []
    
    def run(self, 
            tickers: list[str], 
            start_date: date, 
            end_date: date) -> BacktestResult:
        """
        Запуск бэктеста
        """
        pass
    
    def execute_signal(self, signal: Signal, current_price: float) -> None:
        """
        Исполнение сигнала (лимитный ордер)
        """
        pass
```

**Portfolio** - виртуальный портфель
```python
class Portfolio:
    def __init__(self, initial_capital: float):
        self.cash = initial_capital
        self.positions = {}  # {ticker: quantity}
        self.equity_curve = []
    
    def buy(self, ticker: str, quantity: int, price: float) -> bool:
        pass
    
    def sell(self, ticker: str, quantity: int, price: float) -> bool:
        pass
    
    def get_total_value(self, current_prices: dict) -> float:
        pass
```

---

### 6. Database Models

#### Instrument (Тикер)
```python
class Instrument(Base):
    __tablename__ = "instruments"
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String, unique=True, index=True)
    name = Column(String)
    market = Column(String)  # "MOEX", "CME" и т.д.
    instrument_type = Column(String)  # "stock", "future", "index"
    
    # Связь с индексом
    index_id = Column(Integer, ForeignKey("indexes.id"), nullable=True)
    index = relationship("Index", back_populates="instruments")
```

#### Index (Индекс)
```python
class Index(Base):
    __tablename__ = "indexes"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    ticker = Column(String, unique=True)
    
    instruments = relationship("Instrument", back_populates="index")
```

#### OHLCV (Свечи)
```python
class OHLCV(Base):
    __tablename__ = "ohlcv"
    
    id = Column(Integer, primary_key=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), index=True)
    timeframe = Column(String, index=True)  # "1h", "1d", "1w", "1M"
    timestamp = Column(DateTime, index=True)
    
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(BigInteger)
    
    __table_args__ = (
        UniqueConstraint('instrument_id', 'timeframe', 'timestamp'),
        Index('idx_instrument_timeframe_time', 'instrument_id', 'timeframe', 'timestamp')
    )
```

#### Signal
```python
class Signal(Base):
    __tablename__ = "signals"
    
    id = Column(Integer, primary_key=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id"))
    strategy_name = Column(String)
    signal_type = Column(String)  # "BUY", "SELL"
    timestamp = Column(DateTime)
    price = Column(Float)
    confidence = Column(Float, nullable=True)
    
    # Риск-менеджмент
    position_size = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
```

---

## API Endpoints

### Instruments
```
GET    /api/v1/instruments              # Список инструментов
GET    /api/v1/instruments/{ticker}     # Информация о тикере
POST   /api/v1/instruments              # Добавить тикер
PUT    /api/v1/instruments/{ticker}     # Обновить информацию
DELETE /api/v1/instruments/{ticker}     # Удалить тикер

# Связь с индексами
GET    /api/v1/instruments/{ticker}/index        # Получить индекс тикера
PUT    /api/v1/instruments/{ticker}/index/{index_id}  # Связать с индексом
```

### Data
```
GET    /api/v1/data/{ticker}            # Получить OHLCV
       ?timeframe=1h&start=2024-01-01&end=2024-12-01
POST   /api/v1/data/import              # Импорт из CSV
GET    /api/v1/data/timeframes          # Доступные таймфреймы
```

### Indicators
```
GET    /api/v1/indicators               # Список доступных индикаторов
GET    /api/v1/indicators/{name}        # Описание индикатора
POST   /api/v1/indicators/calculate     # Рассчитать индикатор
       Body: {ticker, timeframe, indicator_config}
```

### Strategies
```
GET    /api/v1/strategies               # Список стратегий
GET    /api/v1/strategies/{name}        # Детали стратегии
POST   /api/v1/strategies               # Создать стратегию
PUT    /api/v1/strategies/{id}          # Обновить стратегию
```

### Signals
```
GET    /api/v1/signals                  # История сигналов
       ?ticker=&start=&end=
POST   /api/v1/signals/generate         # Сгенерировать сигналы
       Body: {strategy_id, tickers, timeframe}
```

### Backtesting
```
POST   /api/v1/backtest/run             # Запустить бэктест
       Body: {strategy_id, tickers, start_date, end_date, initial_capital}
GET    /api/v1/backtest/{id}/results    # Результаты бэктеста
GET    /api/v1/backtest/{id}/trades     # Список сделок
```

---

## Workflow примеры

### 1. Добавление нового тикера и импорт данных

```
1. POST /api/v1/instruments
   {
     "ticker": "GAZP",
     "name": "Газпром",
     "market": "MOEX",
     "instrument_type": "stock"
   }

2. POST /api/v1/data/import
   {
     "ticker": "GAZP",
     "csv_path": "/data/moex/GAZP_1h.csv",
     "timeframe": "1h"
   }

3. PUT /api/v1/instruments/GAZP/index/1
   # Связываем с индексом IMOEX
```

### 2. Создание стратегии с multi-timeframe индикаторами

```python
# Конфигурация стратегии
strategy_config = {
    "name": "My Strategy",
    "indicators": [
        {
            "name": "MA",
            "timeframe": "1d",
            "params": {"period": 50, "ma_type": "SMA"}
        },
        {
            "name": "RSI",
            "timeframe": "1h",
            "params": {"period": 14}
        }
    ],
    "rules": {
        "entry": "close > MA_1d AND RSI_1h < 30",
        "exit": "RSI_1h > 70"
    }
}
```

### 3. Генерация сигналов

```
POST /api/v1/signals/generate
{
  "strategy_id": 1,
  "tickers": ["GAZP", "SBER", "LKOH"],
  "start_date": "2024-01-01",
  "end_date": "2024-12-01"
}
```

### 4. Запуск бэктеста

```
POST /api/v1/backtest/run
{
  "strategy_id": 1,
  "tickers": ["GAZP"],
  "start_date": "2023-01-01",
  "end_date": "2024-01-01",
  "initial_capital": 1000000,
  "commission": 0.0005
}
```

---

## Расширяемость

### Добавление нового индикатора

```python
# backend/app/indicators/custom/my_indicator.py

from app.indicators.base import BaseIndicator, register_indicator
import pandas as pd

@register_indicator
class MyCustomIndicator(BaseIndicator):
    name = "MyIndicator"
    category = "custom"
    
    def __init__(self, param1: int, param2: float, timeframe: str = "1d"):
        self.param1 = param1
        self.param2 = param2
        self.timeframe = timeframe
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        # Ваша логика расчёта
        result = data['close'] * self.param1 / self.param2
        return result
    
    def validate_parameters(self) -> bool:
        return self.param1 > 0 and self.param2 > 0
```

После добавления индикатор автоматически появится в:
- `GET /api/v1/indicators` - списке доступных индикаторов
- Frontend панели выбора индикаторов

### Добавление новой стратегии

```python
# backend/app/strategies/examples/my_strategy.py

from app.strategies.base import BaseStrategy, register_strategy
from app.indicators.technical.moving_average import MovingAverage
from app.models.signal import Signal

@register_strategy
class MyStrategy(BaseStrategy):
    name = "My Custom Strategy"
    description = "Описание стратегии"
    
    def __init__(self):
        self.ma_fast = MovingAverage(period=10, timeframe="1h")
        self.ma_slow = MovingAverage(period=30, timeframe="1d")
        
    def generate_signal(self, data: dict[str, pd.DataFrame]) -> Signal | None:
        hourly = data["1h"]
        daily = data["1d"]
        
        ma_fast_val = self.ma_fast.calculate(hourly).iloc[-1]
        ma_slow_val = self.ma_slow.calculate(daily).iloc[-1]
        
        if ma_fast_val > ma_slow_val:
            return Signal(
                type="BUY",
                price=hourly['close'].iloc[-1],
                timestamp=hourly.index[-1]
            )
        
        return None
```

---

## Миграция CSV → Database

### Структура CSV файлов
```
date,open,high,low,close,volume
2024-01-01 10:00:00,100.5,102.3,99.8,101.2,1000000
2024-01-01 11:00:00,101.2,103.5,101.0,103.0,1200000
```

### Процесс миграции

```python
# Скрипт миграции
from app.utils.csv_importer import CSVImporter

importer = CSVImporter()

# Импорт одного файла
importer.import_file(
    csv_path="data/moex/GAZP_1h.csv",
    ticker="GAZP",
    timeframe="1h"
)

# Массовый импорт
importer.import_directory(
    directory="data/moex/",
    pattern="*_1h.csv",
    timeframe="1h"
)
```

### Валидация данных при импорте
- Проверка формата дат
- Проверка корректности OHLC (O,H,L,C > 0, H >= max(O,C), L <= min(O,C))
- Проверка дубликатов
- Заполнение пропусков

---

## Frontend Architecture

### Конфигурация окружения

```typescript
// src/environments/environment.ts
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/v1',
  wsUrl: 'ws://localhost:8000/ws'
};

// src/environments/environment.production.ts
export const environment = {
  production: true,
  apiUrl: 'https://api.trading-signals.com/api/v1',
  wsUrl: 'wss://api.trading-signals.com/ws'
};
```

### Interceptors

```typescript
// core/interceptors/auth.interceptor.ts
import { HttpInterceptorFn } from '@angular/common/http';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = localStorage.getItem('auth_token');
  
  if (token) {
    req = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
  }
  
  return next(req);
};

// core/interceptors/error.interceptor.ts
import { HttpInterceptorFn } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  return next(req).pipe(
    catchError(error => {
      if (error.status === 401) {
        // Redirect to login
        console.error('Unauthorized');
      }
      
      if (error.status === 500) {
        console.error('Server error:', error.message);
      }
      
      return throwError(() => error);
    })
  );
};
```

### Модульная структура

Angular использует модульный подход с standalone компонентами (Angular 17+):

```typescript
// app.config.ts
import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideAnimations } from '@angular/platform-browser/animations';
import { routes } from './app.routes';
import { authInterceptor } from './core/interceptors/auth.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(withInterceptors([authInterceptor])),
    provideAnimations()
  ]
};
```

### Маршруты

```typescript
// app.routes.ts
import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    redirectTo: '/dashboard',
    pathMatch: 'full'
  },
  {
    path: 'dashboard',
    loadComponent: () => import('./features/dashboard/dashboard.component')
      .then(m => m.DashboardComponent)
  },
  {
    path: 'analysis',
    loadChildren: () => import('./features/analysis/analysis.routes')
      .then(m => m.ANALYSIS_ROUTES)
  },
  {
    path: 'signals',
    loadChildren: () => import('./features/signals/signals.routes')
      .then(m => m.SIGNALS_ROUTES)
  },
  {
    path: 'backtesting',
    loadChildren: () => import('./features/backtesting/backtesting.routes')
      .then(m => m.BACKTESTING_ROUTES)
  }
];
```

### Страницы

**Dashboard** - главная страница
- Обзор портфеля
- Последние сигналы
- График equity curve

**Analysis** - анализ инструментов
- График с индикаторами
- Выбор тикера и таймфрейма
- Добавление индикаторов на график
- Multi-timeframe индикаторы

**Signals** - сигналы
- Фильтр по тикерам, датам, стратегиям
- Таблица сигналов
- Детали каждого сигнала

**Backtesting** - бэктестинг
- Конфигурация бэктеста
- Запуск и результаты
- График equity curve
- Список сделок

### Сервисы

#### API Service
```typescript
// core/services/api.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Instrument, Signal, BacktestResult } from '../../shared/models';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  // Instruments
  getInstruments(): Observable<Instrument[]> {
    return this.http.get<Instrument[]>(`${this.apiUrl}/instruments`);
  }

  getInstrument(ticker: string): Observable<Instrument> {
    return this.http.get<Instrument>(`${this.apiUrl}/instruments/${ticker}`);
  }

  // Data
  getOHLCV(ticker: string, timeframe: string, start: string, end: string): Observable<any> {
    const params = new HttpParams()
      .set('timeframe', timeframe)
      .set('start', start)
      .set('end', end);
    
    return this.http.get(`${this.apiUrl}/data/${ticker}`, { params });
  }

  // Indicators
  calculateIndicator(config: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/indicators/calculate`, config);
  }

  // Signals
  generateSignals(config: any): Observable<Signal[]> {
    return this.http.post<Signal[]>(`${this.apiUrl}/signals/generate`, config);
  }

  // Backtesting
  runBacktest(config: any): Observable<BacktestResult> {
    return this.http.post<BacktestResult>(`${this.apiUrl}/backtest/run`, config);
  }
}
```

#### Instruments Service (с State)
```typescript
// features/instruments/services/instruments.service.ts
import { Injectable, signal, computed } from '@angular/core';
import { ApiService } from '../../../core/services/api.service';
import { Instrument } from '../../../shared/models';
import { tap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class InstrumentsService {
  private instruments = signal<Instrument[]>([]);
  private selectedTicker = signal<string | null>(null);

  // Computed signals
  instrumentsList = computed(() => this.instruments());
  selectedInstrument = computed(() => 
    this.instruments().find(i => i.ticker === this.selectedTicker())
  );

  constructor(private api: ApiService) {}

  loadInstruments() {
    return this.api.getInstruments().pipe(
      tap(instruments => this.instruments.set(instruments))
    );
  }

  selectInstrument(ticker: string) {
    this.selectedTicker.set(ticker);
  }

  addInstrument(instrument: Instrument) {
    return this.api.createInstrument(instrument).pipe(
      tap(newInstrument => {
        this.instruments.update(list => [...list, newInstrument]);
      })
    );
  }
}
```

### Компоненты

#### Candlestick Chart Component
```typescript
// features/analysis/components/chart/candlestick-chart.component.ts
import { Component, Input, OnInit, OnChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NgxEchartsModule } from 'ngx-echarts';
import { EChartsOption } from 'echarts';

@Component({
  selector: 'app-candlestick-chart',
  standalone: true,
  imports: [CommonModule, NgxEchartsModule],
  template: `
    <div echarts [options]="chartOption" class="chart-container"></div>
  `,
  styles: [`
    .chart-container {
      height: 600px;
      width: 100%;
    }
  `]
})
export class CandlestickChartComponent implements OnInit, OnChanges {
  @Input() ohlcvData: any[] = [];
  @Input() indicators: any[] = [];
  @Input() signals: any[] = [];

  chartOption: EChartsOption = {};

  ngOnInit() {
    this.updateChart();
  }

  ngOnChanges() {
    this.updateChart();
  }

  private updateChart() {
    const categoryData = this.ohlcvData.map(d => d.timestamp);
    const candlestickData = this.ohlcvData.map(d => [d.open, d.close, d.low, d.high]);
    
    const series: any[] = [
      {
        type: 'candlestick',
        data: candlestickData,
        itemStyle: {
          color: '#26a69a',
          color0: '#ef5350',
          borderColor: '#26a69a',
          borderColor0: '#ef5350'
        }
      }
    ];

    // Добавляем индикаторы
    this.indicators.forEach(indicator => {
      series.push({
        type: 'line',
        name: indicator.name,
        data: indicator.values,
        smooth: true,
        lineStyle: {
          width: 2,
          color: indicator.color
        }
      });
    });

    // Добавляем маркеры сигналов
    if (this.signals.length > 0) {
      series.push({
        type: 'scatter',
        name: 'Signals',
        data: this.signals.map(s => [s.timestamp, s.price]),
        symbolSize: 15,
        itemStyle: {
          color: (params: any) => {
            const signal = this.signals[params.dataIndex];
            return signal.type === 'BUY' ? '#00ff00' : '#ff0000';
          }
        }
      });
    }

    this.chartOption = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross'
        }
      },
      legend: {
        data: ['Candlestick', ...this.indicators.map(i => i.name)],
        top: 10
      },
      grid: {
        left: '10%',
        right: '10%',
        bottom: '15%'
      },
      xAxis: {
        type: 'category',
        data: categoryData,
        scale: true,
        boundaryGap: false,
        axisLine: { onZero: false },
        splitLine: { show: false },
        min: 'dataMin',
        max: 'dataMax'
      },
      yAxis: {
        scale: true,
        splitArea: {
          show: true
        }
      },
      dataZoom: [
        {
          type: 'inside',
          start: 50,
          end: 100
        },
        {
          show: true,
          type: 'slider',
          top: '90%',
          start: 50,
          end: 100
        }
      ],
      series: series
    };
  }
}
```

#### Analysis Component
```typescript
// features/analysis/analysis.component.ts
import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CandlestickChartComponent } from './components/chart/candlestick-chart.component';
import { InstrumentSelectorComponent } from './components/instrument-selector/instrument-selector.component';
import { IndicatorPanelComponent } from './components/indicator-panel/indicator-panel.component';
import { AnalysisService } from './services/analysis.service';

@Component({
  selector: 'app-analysis',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    CandlestickChartComponent,
    InstrumentSelectorComponent,
    IndicatorPanelComponent
  ],
  template: `
    <div class="analysis-container">
      <div class="controls">
        <app-instrument-selector
          [instruments]="instruments()"
          (instrumentSelected)="onInstrumentSelected($event)">
        </app-instrument-selector>
        
        <div class="timeframe-selector">
          <label>Timeframe:</label>
          <select [(ngModel)]="selectedTimeframe" (change)="loadData()">
            <option value="1h">1 Hour</option>
            <option value="1d">1 Day</option>
            <option value="1w">1 Week</option>
            <option value="1M">1 Month</option>
          </select>
        </div>
      </div>

      <div class="main-content">
        <app-indicator-panel
          [availableIndicators]="availableIndicators()"
          [activeIndicators]="activeIndicators()"
          (indicatorAdded)="onIndicatorAdded($event)"
          (indicatorRemoved)="onIndicatorRemoved($event)">
        </app-indicator-panel>

        <app-candlestick-chart
          [ohlcvData]="ohlcvData()"
          [indicators]="indicatorData()"
          [signals]="signals()">
        </app-candlestick-chart>
      </div>

      @if (loading()) {
        <div class="loader">Loading...</div>
      }
    </div>
  `,
  styles: [`
    .analysis-container {
      padding: 20px;
    }
    .controls {
      display: flex;
      gap: 20px;
      margin-bottom: 20px;
    }
    .main-content {
      display: grid;
      grid-template-columns: 300px 1fr;
      gap: 20px;
    }
    .loader {
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
    }
  `]
})
export class AnalysisComponent implements OnInit {
  instruments = signal<any[]>([]);
  selectedTicker = signal<string | null>(null);
  selectedTimeframe = '1d';
  
  ohlcvData = signal<any[]>([]);
  indicatorData = signal<any[]>([]);
  signals = signal<any[]>([]);
  
  availableIndicators = signal<any[]>([]);
  activeIndicators = signal<any[]>([]);
  
  loading = signal(false);

  constructor(private analysisService: AnalysisService) {}

  ngOnInit() {
    this.loadInstruments();
    this.loadAvailableIndicators();
  }

  loadInstruments() {
    this.analysisService.getInstruments().subscribe(
      instruments => this.instruments.set(instruments)
    );
  }

  loadAvailableIndicators() {
    this.analysisService.getAvailableIndicators().subscribe(
      indicators => this.availableIndicators.set(indicators)
    );
  }

  onInstrumentSelected(ticker: string) {
    this.selectedTicker.set(ticker);
    this.loadData();
  }

  loadData() {
    const ticker = this.selectedTicker();
    if (!ticker) return;

    this.loading.set(true);
    
    this.analysisService.getOHLCV(ticker, this.selectedTimeframe).subscribe({
      next: (data) => {
        this.ohlcvData.set(data);
        this.recalculateIndicators();
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Error loading data:', err);
        this.loading.set(false);
      }
    });
  }

  onIndicatorAdded(indicator: any) {
    this.activeIndicators.update(list => [...list, indicator]);
    this.recalculateIndicators();
  }

  onIndicatorRemoved(indicatorName: string) {
    this.activeIndicators.update(list => 
      list.filter(i => i.name !== indicatorName)
    );
    this.indicatorData.update(list => 
      list.filter(i => i.name !== indicatorName)
    );
  }

  recalculateIndicators() {
    const ticker = this.selectedTicker();
    if (!ticker) return;

    this.activeIndicators().forEach(indicator => {
      this.analysisService.calculateIndicator({
        ticker,
        timeframe: this.selectedTimeframe,
        indicator: indicator.name,
        params: indicator.params
      }).subscribe(result => {
        this.indicatorData.update(list => {
          const filtered = list.filter(i => i.name !== indicator.name);
          return [...filtered, result];
        });
      });
    });
  }
}
```

### State Management (NgRx опционально)

Для более сложного управления состоянием можно использовать NgRx:

```typescript
// store/actions/instruments.actions.ts
import { createAction, props } from '@ngrx/store';
import { Instrument } from '../../shared/models';

export const loadInstruments = createAction(
  '[Instruments] Load Instruments'
);

export const loadInstrumentsSuccess = createAction(
  '[Instruments] Load Instruments Success',
  props<{ instruments: Instrument[] }>()
);

export const loadInstrumentsFailure = createAction(
  '[Instruments] Load Instruments Failure',
  props<{ error: any }>()
);

export const selectInstrument = createAction(
  '[Instruments] Select Instrument',
  props<{ ticker: string }>()
);
```

```typescript
// store/reducers/instruments.reducer.ts
import { createReducer, on } from '@ngrx/store';
import * as InstrumentsActions from '../actions/instruments.actions';
import { Instrument } from '../../shared/models';

export interface InstrumentsState {
  instruments: Instrument[];
  selectedTicker: string | null;
  loading: boolean;
  error: any;
}

export const initialState: InstrumentsState = {
  instruments: [],
  selectedTicker: null,
  loading: false,
  error: null
};

export const instrumentsReducer = createReducer(
  initialState,
  on(InstrumentsActions.loadInstruments, state => ({
    ...state,
    loading: true
  })),
  on(InstrumentsActions.loadInstrumentsSuccess, (state, { instruments }) => ({
    ...state,
    instruments,
    loading: false,
    error: null
  })),
  on(InstrumentsActions.loadInstrumentsFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),
  on(InstrumentsActions.selectInstrument, (state, { ticker }) => ({
    ...state,
    selectedTicker: ticker
  }))
);
```

### Пример Backtesting Component

```typescript
// features/backtesting/backtesting.component.ts
import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { BacktestingService } from './services/backtesting.service';
import { BacktestResultsComponent } from './components/backtest-results/backtest-results.component';

@Component({
  selector: 'app-backtesting',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    BacktestResultsComponent
  ],
  template: `
    <div class="backtesting-container">
      <h1>Backtesting</h1>

      <div class="config-section">
        <h2>Configuration</h2>
        <form [formGroup]="configForm" (ngSubmit)="runBacktest()">
          <div class="form-group">
            <label>Strategy:</label>
            <select formControlName="strategy">
              @for (strategy of strategies(); track strategy.id) {
                <option [value]="strategy.id">{{ strategy.name }}</option>
              }
            </select>
          </div>

          <div class="form-group">
            <label>Ticker:</label>
            <select formControlName="ticker">
              @for (instrument of instruments(); track instrument.ticker) {
                <option [value]="instrument.ticker">{{ instrument.name }}</option>
              }
            </select>
          </div>

          <div class="form-group">
            <label>Start Date:</label>
            <input type="date" formControlName="startDate">
          </div>

          <div class="form-group">
            <label>End Date:</label>
            <input type="date" formControlName="endDate">
          </div>

          <div class="form-group">
            <label>Initial Capital:</label>
            <input type="number" formControlName="initialCapital">
          </div>

          <button type="submit" [disabled]="configForm.invalid || loading()">
            {{ loading() ? 'Running...' : 'Run Backtest' }}
          </button>
        </form>
      </div>

      @if (backtestResult()) {
        <app-backtest-results [result]="backtestResult()!"></app-backtest-results>
      }
    </div>
  `,
  styles: [`
    .backtesting-container {
      padding: 20px;
    }
    .config-section {
      background: #f5f5f5;
      padding: 20px;
      border-radius: 8px;
      margin-bottom: 30px;
    }
    .form-group {
      margin-bottom: 15px;
    }
    .form-group label {
      display: block;
      margin-bottom: 5px;
      font-weight: 600;
    }
    .form-group input,
    .form-group select {
      width: 100%;
      padding: 8px;
      border: 1px solid #ddd;
      border-radius: 4px;
    }
    button {
      padding: 10px 20px;
      background: #007bff;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }
    button:disabled {
      background: #ccc;
      cursor: not-allowed;
    }
  `]
})
export class BacktestingComponent implements OnInit {
  configForm: FormGroup;
  
  strategies = signal<any[]>([]);
  instruments = signal<any[]>([]);
  backtestResult = signal<any>(null);
  loading = signal(false);

  constructor(
    private fb: FormBuilder,
    private backtestingService: BacktestingService
  ) {
    this.configForm = this.fb.group({
      strategy: ['', Validators.required],
      ticker: ['', Validators.required],
      startDate: ['', Validators.required],
      endDate: ['', Validators.required],
      initialCapital: [1000000, [Validators.required, Validators.min(0)]]
    });
  }

  ngOnInit() {
    this.loadStrategies();
    this.loadInstruments();
  }

  loadStrategies() {
    this.backtestingService.getStrategies().subscribe(
      strategies => this.strategies.set(strategies)
    );
  }

  loadInstruments() {
    this.backtestingService.getInstruments().subscribe(
      instruments => this.instruments.set(instruments)
    );
  }

  runBacktest() {
    if (this.configForm.invalid) return;

    this.loading.set(true);
    const config = this.configForm.value;

    this.backtestingService.runBacktest(config).subscribe({
      next: (result) => {
        this.backtestResult.set(result);
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Backtest error:', err);
        this.loading.set(false);
      }
    });
  }
}
```

### Компоненты графиков

Используем **ngx-echarts** для интеграции Apache ECharts с Angular:

```bash
npm install echarts ngx-echarts
```

```typescript
// angular.json - добавить в assets
"assets": [
  {
    "glob": "**/*",
    "input": "./node_modules/echarts/dist",
    "output": "/assets/echarts/"
  }
]
```

```typescript
// app.config.ts
import { provideEcharts } from 'ngx-echarts';

export const appConfig: ApplicationConfig = {
  providers: [
    // ... другие providers
    provideEcharts()
  ]
};
```

---

## Deployment

### Локальная разработка

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
ng serve
# или для production build
ng build --configuration production
```

### Docker Compose

```yaml
version: '3.8'

services:
  postgres:
    image: timescale/timescaledb:latest-pg16
    environment:
      POSTGRES_DB: trading_signals
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://user:password@postgres:5432/trading_signals
    volumes:
      - ./backend:/app
      - ./data:/data
    ports:
      - "8000:8000"
    depends_on:
      - postgres

  frontend:
    build: ./frontend
    ports:
      - "4200:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

#### Dockerfile для Angular Frontend

```dockerfile
# frontend/Dockerfile
FROM node:20-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build -- --configuration production

FROM nginx:alpine
COPY --from=build /app/dist/trading-signals-frontend/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### nginx.conf для Angular

```nginx
# frontend/nginx.conf
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

---

## Этапы разработки (Roadmap)

### Фаза 1: MVP (2-3 недели)
- [x] Структура проекта
- [ ] Модели данных и миграции БД
- [ ] CSV импорт
- [ ] Базовые технические индикаторы (MA, RSI, MACD)
- [ ] Простой график с candlestick
- [ ] API endpoints для данных и индикаторов

### Фаза 2: Сигналы (2 недели)
- [ ] Система стратегий
- [ ] Генератор сигналов
- [ ] Базовый риск-менеджмент
- [ ] Frontend для просмотра сигналов
- [ ] Связывание тикеров с индексами

### Фаза 3: Бэктестинг (2 недели)
- [ ] Движок бэктестинга
- [ ] Виртуальный портфель
- [ ] Исполнение лимитных ордеров
- [ ] Отчёты и визуализация результатов
- [ ] Frontend для бэктестов

### Фаза 4: Multi-timeframe (1-2 недели)
- [ ] TimeframeManager
- [ ] Поддержка индикаторов из разных таймфреймов
- [ ] Синхронизация данных
- [ ] UI для multi-timeframe анализа

### Фаза 5: Оптимизация и расширение
- [ ] Кэширование индикаторов (Redis)
- [ ] Оптимизация запросов к БД
- [ ] Дополнительные индикаторы
- [ ] Экспорт отчётов (PDF, Excel)
- [ ] Поддержка американского рынка

---

## Заметки по производительности

### Оптимизация расчётов индикаторов
- Кэшировать результаты расчётов индикаторов
- Использовать векторизацию (NumPy/Pandas)
- Рассчитывать только новые бары при инкрементальном обновлении

### База данных
- Индексы на (instrument_id, timeframe, timestamp)
- Партиционирование таблицы OHLCV по времени (TimescaleDB)
- Периодическая очистка старых данных

### Frontend
- Виртуализация списков (большие таблицы)
- Lazy loading графиков
- Debounce на фильтрах

---

## Безопасность

- Валидация всех входных данных (Pydantic)
- Rate limiting на API
- CORS настройки для локального использования
- Логирование всех операций
- Backup базы данных

---

## Тестирование

### Backend (Python)

```python
# Пример unit теста индикатора
def test_moving_average():
    data = pd.DataFrame({
        'close': [100, 102, 101, 103, 105]
    })
    
    ma = MovingAverage(period=3)
    result = ma.calculate(data)
    
    assert result.iloc[-1] == pytest.approx(103.0)

# Пример теста стратегии
def test_strategy_signal_generation():
    strategy = MyStrategy()
    data = {
        "1h": hourly_dataframe,
        "1d": daily_dataframe
    }
    
    signal = strategy.generate_signal(data)
    
    assert signal.type == "BUY"
    assert signal.price > 0
```

### Frontend (Angular)

```typescript
// Пример unit теста компонента
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AnalysisComponent } from './analysis.component';
import { AnalysisService } from './services/analysis.service';
import { of } from 'rxjs';

describe('AnalysisComponent', () => {
  let component: AnalysisComponent;
  let fixture: ComponentFixture<AnalysisComponent>;
  let analysisService: jasmine.SpyObj<AnalysisService>;

  beforeEach(async () => {
    const analysisSpy = jasmine.createSpyObj('AnalysisService', [
      'getInstruments',
      'getOHLCV'
    ]);

    await TestBed.configureTestingModule({
      imports: [AnalysisComponent],
      providers: [
        { provide: AnalysisService, useValue: analysisSpy }
      ]
    }).compileComponents();

    analysisService = TestBed.inject(AnalysisService) as jasmine.SpyObj<AnalysisService>;
    fixture = TestBed.createComponent(AnalysisComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load instruments on init', () => {
    const mockInstruments = [
      { ticker: 'GAZP', name: 'Газпром' },
      { ticker: 'SBER', name: 'Сбербанк' }
    ];
    
    analysisService.getInstruments.and.returnValue(of(mockInstruments));
    
    component.ngOnInit();
    
    expect(analysisService.getInstruments).toHaveBeenCalled();
    expect(component.instruments()).toEqual(mockInstruments);
  });

  it('should load data when instrument is selected', () => {
    const mockData = [
      { timestamp: '2024-01-01', open: 100, high: 105, low: 99, close: 103, volume: 1000 }
    ];
    
    analysisService.getOHLCV.and.returnValue(of(mockData));
    
    component.onInstrumentSelected('GAZP');
    
    expect(analysisService.getOHLCV).toHaveBeenCalledWith('GAZP', '1d');
    expect(component.ohlcvData()).toEqual(mockData);
  });
});

// Пример теста сервиса
import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ApiService } from './api.service';

describe('ApiService', () => {
  let service: ApiService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [ApiService]
    });
    
    service = TestBed.inject(ApiService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should fetch instruments', () => {
    const mockInstruments = [
      { ticker: 'GAZP', name: 'Газпром' }
    ];

    service.getInstruments().subscribe(instruments => {
      expect(instruments).toEqual(mockInstruments);
    });

    const req = httpMock.expectOne(`${service['apiUrl']}/instruments`);
    expect(req.request.method).toBe('GET');
    req.flush(mockInstruments);
  });
});
```

---

## Дополнительные возможности (будущее)

- Real-time обработка через WebSocket
- Telegram/Email уведомления о сигналах
- Интеграция с брокерами (MOEX ISS API, Tinkoff API)
- Machine Learning для предсказаний
- Sentiment анализ новостей
- Portfolio optimization
- Multi-account support

---

## Полезные библиотеки

### Python
- **ta-lib** - технические индикаторы
- **pandas-ta** - альтернатива ta-lib
- **vectorbt** - векторизованный бэктестинг
- **yfinance** - загрузка данных (для американского рынка)
- **moexalgo** - API Московской биржи

### JavaScript/TypeScript
- **ngx-echarts** - Angular wrapper для ECharts
- **@ngrx/store** - state management
- **@ngrx/effects** - side effects для NgRx
- **rxjs** - реактивное программирование
- **date-fns** - работа с датами
- **Angular Material** или **PrimeNG** - UI компоненты
- **class-validator** - валидация данных

---

## Контакты и поддержка

Для вопросов и предложений:
- GitHub Issues
- Email: support@trading-signals.local

---

**Версия документа:** 1.0  
**Дата:** 2024-12-01  
**Автор:** AI Assistant