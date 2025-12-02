# План реализации системы торговых сигналов

## Обзор

Пошаговый план разработки системы анализа торговых данных с генерацией сигналов и бэктестингом.

**Технологии:** Python 3.11+, FastAPI, PostgreSQL (TimescaleDB), Angular 17+, Redis

---

## Фаза 0: Инициализация проекта (1-2 дня) ✅

### 0.1 Настройка окружения разработки

- [x] Создать структуру каталогов проекта
  - `backend/app/` - основной код бэкенда
  - `frontend/src/` - код фронтенда
  - `data/` - CSV файлы
  - `migrations/` - миграции БД
  - `tests/` - тесты

- [x] Настроить Backend
  - [x] Создать `requirements.txt` с зависимостями:
    - fastapi, uvicorn
    - sqlalchemy, alembic
    - pydantic, pydantic-settings
    - pandas, numpy
    - ta-lib или pandas-ta
    - psycopg2-binary
    - redis (опционально)
    - pytest, pytest-asyncio
  - [x] Создать виртуальное окружение Python
  - [x] Инициализировать `pyproject.toml`

- [ ] Настроить Frontend
  - [ ] Создать Angular проект: `ng new trading-signals-frontend --standalone`
  - [ ] Добавить зависимости в `package.json`:
    - `@angular/core@^17.0.0`
    - `ngx-echarts`, `echarts`
    - `@ngrx/store`, `@ngrx/effects` (опционально)
  - [ ] Настроить `tsconfig.json` (strict mode)
  - [ ] Настроить `angular.json` (environments)

- [x] Настроить инфраструктуру
  - [x] Создать `docker-compose.yml` для PostgreSQL + TimescaleDB
  - [x] Создать `.env.example` с переменными окружения
  - [x] Создать `.gitignore`
  - [x] Настроить Alembic для миграций БД

- [x] Настроить Git
  - [x] Инициализировать репозиторий
  - [x] Создать `.gitignore`
  - [x] Первый коммит с базовой структурой

---

## Фаза 1: Основа Backend (MVP) (1 неделя) 🔄

### 1.1 Модели базы данных ✅

**Файлы:** `backend/app/models/`

- [x] `database.py` - настройка подключения к БД
  - [x] Создать `engine` и `SessionLocal`
  - [x] Базовый класс `Base` для моделей
  - [x] Dependency `get_db()` для FastAPI

- [x] `instrument.py` - модель инструмента
  ```python
  class Instrument(Base):
      id, ticker, name, market, instrument_type
      index_id (ForeignKey), index (relationship)
  ```

- [x] `index.py` - модель индекса
  ```python
  class Index(Base):
      id, name, ticker
      instruments (relationship)
  ```

- [x] `ohlcv.py` - модель свечей
  ```python
  class OHLCV(Base):
      id, instrument_id, timeframe, timestamp
      open, high, low, close, volume
      UniqueConstraint + Indexes
  ```

- [x] `signal.py` - модель сигнала
  ```python
  class Signal(Base):
      id, instrument_id, strategy_name, signal_type
      timestamp, price, confidence
      position_size, stop_loss, take_profit
  ```

- [x] `strategy.py` - модель стратегии
  ```python
  class Strategy(Base):
      id, name, description, config (JSON)
      created_at, updated_at
  ```

- [x] Создать первую миграцию Alembic
  ```bash
  alembic init migrations
  alembic revision --autogenerate -m "Initial models"
  alembic upgrade head
  ```

- [ ] **Тесты:** `tests/unit/test_models.py`
  - [ ] Тест создания инструмента
  - [ ] Тест связи инструмента с индексом
  - [ ] Тест UniqueConstraint для OHLCV

### 1.2 Pydantic схемы ✅

**Файлы:** `backend/app/schemas/`

- [x] `instrument.py`
  - [x] `InstrumentBase`, `InstrumentCreate`, `InstrumentUpdate`
  - [x] `InstrumentRead` (с данными индекса)

- [x] `signal.py`
  - [x] `SignalBase`, `SignalCreate`, `SignalRead`

- [x] `indicator.py`
  - [x] `IndicatorConfig`, `IndicatorResult`

- [x] `backtest.py`
  - [x] `BacktestConfig`, `BacktestResult`, `Trade`

- [ ] **Тесты:** валидация схем с pytest

### 1.3 Конфигурация приложения ✅

**Файлы:** `backend/app/config.py`

- [x] Класс `Settings` (Pydantic BaseSettings)
  - [x] `DATABASE_URL`
  - [x] `REDIS_URL` (опционально)
  - [x] `API_V1_PREFIX = "/api/v1"`
  - [x] `DEBUG_MODE`
  - [x] CORS настройки

### 1.4 Основное FastAPI приложение ✅

**Файлы:** `backend/app/main.py`

- [x] Создать FastAPI app
- [x] Настроить CORS middleware
- [x] Подключить роутеры (пока пустые)
- [x] Настроить обработку ошибок
- [x] Health check endpoint: `GET /health`

- [ ] **Тест:** запустить сервер, проверить `/health`

### 1.5 Data Management Layer ✅

**Файлы:** `backend/app/core/`

- [x] `data_loader.py`
  ```python
  class DataLoader:
      def load_from_csv(ticker, timeframe, path) -> pd.DataFrame
      def load_from_db(ticker, timeframe, start, end) -> pd.DataFrame
      def migrate_csv_to_db(csv_path, ticker) -> None
  ```
  - [x] Реализовать чтение CSV (pandas)
  - [x] Реализовать загрузку из БД (SQLAlchemy)
  - [x] Валидация формата CSV

- [x] `data_validator.py` (в `utils/`)
  - [x] Проверка формата дат
  - [x] Проверка OHLC корректности: H >= max(O,C), L <= min(O,C)
  - [x] Проверка дубликатов
  - [x] Обработка пропусков (forward fill)

- [x] `csv_importer.py` (в `utils/`)
  ```python
  class CSVImporter:
      def import_file(csv_path, ticker, timeframe) -> None
      def import_directory(directory, pattern, timeframe) -> None
  ```

- [x] `data_manager.py` - управление данными
  - [x] Multi-timeframe support
  - [x] Resampling между таймфреймами

- [ ] **Тесты:**
  - [ ] `test_data_loader.py` - загрузка из CSV и БД
  - [ ] `test_data_validator.py` - валидация данных
  - [ ] Использовать fixtures с тестовыми CSV

---

## Фаза 2: API Endpoints (MVP) ✅ (3-4 дня)

### 2.1 API для инструментов ✅

**Файлы:** `backend/app/api/v1/instruments.py`

- [x] `GET /api/v1/instruments` - список всех инструментов
- [x] `GET /api/v1/instruments/{ticker}` - информация о тикере
- [x] `POST /api/v1/instruments` - добавить тикер
- [x] `PUT /api/v1/instruments/{ticker}` - обновить
- [x] `DELETE /api/v1/instruments/{ticker}` - удалить
- [x] `GET /api/v1/instruments/indexes/` - список индексов
- [x] `GET /api/v1/instruments/indexes/{index_id}` - информация об индексе
- [x] `POST /api/v1/instruments/indexes/` - создать индекс
- [x] `PUT /api/v1/instruments/indexes/{index_id}` - обновить индекс
- [x] `DELETE /api/v1/instruments/indexes/{index_id}` - удалить индекс
- [x] `PUT /api/v1/instruments/{ticker}/index/{index_id}` - связать с индексом

- [ ] **Тесты:** integration тесты с TestClient (FastAPI)

### 2.2 API для данных ✅

**Файлы:** `backend/app/api/v1/data.py`

- [x] `GET /api/v1/data/{ticker}` - получить OHLCV
  - Query параметры: `timeframe`, `start`, `end`, `limit`
  - Возвращать JSON массив свечей

- [x] `POST /api/v1/data/import` - импорт из CSV
  - Body: `{ticker, csv_path, timeframe, create_instrument, ...}`
  - Запуск CSVImporter

- [x] `POST /api/v1/data/import/batch` - массовый импорт из директории
  - Автоматическое извлечение тикера из имени файла

- [x] `GET /api/v1/data/timeframes/` - список доступных таймфреймов
  - Возвращать: `["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w", "1M"]`

- [x] `GET /api/v1/data/{ticker}/latest` - получить последнюю свечу

- [x] `DELETE /api/v1/data/{ticker}` - удалить OHLCV данные

- [ ] **Тесты:**
  - [ ] Тест получения OHLCV данных
  - [ ] Тест импорта CSV
  - [ ] Использовать тестовую БД

### 2.3 Dependencies ✅

**Файлы:** `backend/app/api/deps.py`

- [x] `get_db()` - dependency для БД сессии
- [x] Placeholders для будущей аутентификации

### 2.4 Интеграция в FastAPI ✅

- [x] Обновлён `main.py` с подключением роутеров
- [x] API versioning через `/api/v1`
- [x] Swagger UI документация (автоматически)

---

## Фаза 3: Система индикаторов ✅ (4-5 дней)

### 3.1 Базовый класс индикатора ✅

**Файлы:** `backend/app/indicators/base.py`

- [x] Абстрактный класс `BaseIndicator`
  - [x] Атрибуты: name, category, description, timeframe, parameters
  - [x] Метод calculate() - абстрактный
  - [x] Метод get_parameters_schema() - абстрактный
  - [x] Валидация параметров (_validate_parameters)
  - [x] Валидация данных (_validate_data)
  - [x] Метод get_info() для метаданных

- [x] IndicatorParameter - Pydantic модель для описания параметров
- [x] IndicatorError - кастомное исключение

### 3.2 Реестр индикаторов ✅

**Файлы:** `backend/app/indicators/registry.py`

- [x] Класс `IndicatorRegistry`
  - [x] register() - регистрация индикатора
  - [x] get() - получение класса по имени
  - [x] get_all() - все индикаторы
  - [x] list_names() - список названий
  - [x] get_by_category() - фильтр по категории
  - [x] get_info() - метаданные индикатора
  - [x] get_all_info() - метаданные всех индикаторов
  - [x] create_indicator() - создание экземпляра

- [x] Декоратор `@register_indicator` для автоматической регистрации

### 3.3 Технические индикаторы ✅

**Файлы:** `backend/app/indicators/technical/`

- [x] `moving_average.py`
  - [x] MA (Simple Moving Average)
  - [x] EMA (Exponential Moving Average)
  - [x] Параметры: period, source

- [x] `rsi.py`
  - [x] RSI (Relative Strength Index)
  - [x] Параметры: period, source

- [x] `stochastic.py`
  - [x] Stochastic Oscillator
  - [x] Параметры: k_period, d_period, smooth_k

- [x] `macd.py`
  - [x] MACD (Moving Average Convergence Divergence)
  - [x] Возвращает: macd, signal, histogram
  - [x] Параметры: fast_period, slow_period, signal_period, source

- [x] `adx.py`
  - [x] ADX (Average Directional Index)
  - [x] Возвращает: adx, plus_di, minus_di
  - [x] Параметры: period

- [x] `bollinger_bands.py`
  - [x] Bollinger Bands
  - [x] Возвращает: upper, middle, lower
  - [x] Параметры: period, std_dev, source

- [x] `atr.py`
  - [x] ATR (Average True Range)
  - [x] Параметры: period

- [ ] **Тесты:** `tests/unit/test_indicators.py`
  - [ ] Тест расчёта каждого индикатора
  - [ ] Сравнение с известными значениями
  - [ ] Тест валидации параметров

### 3.4 Кастомные индикаторы ✅

**Файлы:** `backend/app/indicators/custom/`

- [x] `market_regime.py`
  - [x] MarketRegime - определение режима рынка
  - [x] Возвращает: "trending", "ranging", "volatile"
  - [x] Использует ADX и ATR
  - [x] Параметры: period, adx_threshold

- [x] `support_resistance.py`
  - [x] SupportResistance - уровни поддержки/сопротивления
  - [x] Поиск локальных экстремумов
  - [x] Кластеризация близких уровней
  - [x] Параметры: window, num_levels, tolerance

### 3.5 API для индикаторов ✅

**Файлы:** `backend/app/api/v1/indicators.py`

- [x] `GET /api/v1/indicators/` - список доступных индикаторов
  - [x] Возвращает IndicatorListResponse с метаданными

- [x] `GET /api/v1/indicators/{name}` - описание индикатора
  - [x] Параметры, категория, документация

- [x] `GET /api/v1/indicators/category/{category}` - индикаторы по категории

- [x] `POST /api/v1/indicators/calculate` - рассчитать индикатор
  - [x] Body: IndicatorCalculateRequest
  - [x] Возвращает: IndicatorCalculateResponse с результатами

- [x] `POST /api/v1/indicators/calculate/multiple` - расчёт нескольких индикаторов

- [x] `GET /api/v1/indicators/stats/usage` - статистика по индикаторам

- [x] Обновлён main.py с подключением роутера

- [ ] **Тесты:** integration тесты расчёта через API

---

## Фаза 4: Timeframe Manager ✅ (2-3 дня)

### 4.1 Утилиты для таймфреймов ✅

**Файлы:** `backend/app/utils/timeframe_utils.py`

- [x] Класс `TimeframeUtils`
  - [x] validate_timeframe() - валидация таймфрейма
  - [x] get_timeframe_minutes() - конвертация в минуты
  - [x] get_timeframe_offset() - конвертация в pandas offset
  - [x] get_timeframe_timedelta() - конвертация в timedelta
  - [x] compare_timeframes() - сравнение таймфреймов
  - [x] is_higher_timeframe() - проверка иерархии
  - [x] get_higher_timeframes() - список более высоких TF
  - [x] get_lower_timeframes() - список более низких TF
  - [x] can_resample() - проверка возможности ресемплинга
  - [x] get_multiplier() - множитель для конвертации
  - [x] sort_timeframes() - сортировка таймфреймов

- [x] Маппинги:
  - [x] TIMEFRAME_TO_MINUTES
  - [x] TIMEFRAME_TO_OFFSET
  - [x] TIMEFRAME_ORDER

### 4.2 Менеджер таймфреймов ✅

**Файлы:** `backend/app/core/timeframe_manager.py`

- [x] Класс `TimeframeManager`
  - [x] align_timeframes() - выравнивание данных разных TF
  - [x] get_higher_timeframe_value() - получение значения с высокого TF
  - [x] resample_ohlcv() - ресемплинг OHLCV данных
  - [x] validate_multi_timeframe_data() - валидация данных
  - [x] get_synchronized_timestamps() - синхронизация временных меток
  - [x] merge_multi_timeframe_indicators() - объединение индикаторов

- [x] Выравнивание данных разных таймфреймов
  - [x] Синхронизация по времени
  - [x] Forward fill для более высоких таймфреймов
  - [x] Автоопределение базового таймфрейма

- [x] Обновлены __init__.py для экспорта

- [ ] **Тесты:**
  - [ ] Тест ресемплинга (1h -> 1d)
  - [ ] Тест выравнивания 2+ таймфреймов
  - [ ] Тест получения значения высшего ТФ
  - [ ] Тест merge_multi_timeframe_indicators

### 4.3 Data Manager с multi-timeframe ✅

**Файлы:** `backend/app/core/data_manager.py`

- [x] Класс `DataManager` (создан в Фазе 1)
  - [x] get_data() - получение данных для одного TF
  - [x] get_multi_timeframe_data() - для нескольких TF
  - [x] save_data() - сохранение данных
  - [x] resample_timeframe() - ресемплинг

- [x] Multi-timeframe поддержка уже реализована

- [ ] **Тесты:** тест загрузки multi-timeframe данных

---

## Фаза 5: Система стратегий ✅ (3-4 дня)

### 5.1 Базовый класс стратегии ✅

**Файлы:** `backend/app/strategies/base.py`

- [x] Абстрактный класс `BaseStrategy`
  - [x] Атрибуты: name, description, version
  - [x] _setup_indicators() - абстрактный метод
  - [x] generate_signal() - абстрактный метод
  - [x] add_indicator() - добавление индикатора в конфигурацию
  - [x] required_timeframes() - список необходимых таймфреймов
  - [x] calculate_indicators() - расчёт всех индикаторов
  - [x] validate_data() - валидация входных данных

- [x] IndicatorConfig - конфигурация индикаторов
  - [x] name, timeframe, parameters, alias

- [x] Signal - модель торгового сигнала
  - [x] signal_type: BUY, SELL, HOLD
  - [x] Риск-менеджмент: stop_loss, take_profit, position_size
  - [x] Метаданные: confidence, reason, metadata

- [x] StrategyError - кастомное исключение

### 5.2 Реестр стратегий ✅

**Файлы:** `backend/app/strategies/registry.py`

- [x] Класс `StrategyRegistry`
  - [x] register() - регистрация стратегии
  - [x] get() - получение класса по имени
  - [x] get_all() - все стратегии
  - [x] list_names() - список названий
  - [x] get_info() - метаданные стратегии
  - [x] get_all_info() - метаданные всех стратегий
  - [x] create_strategy() - создание экземпляра

- [x] Декоратор `@register_strategy` для автоматической регистрации

### 5.3 Примеры стратегий ✅

**Файлы:** `backend/app/strategies/examples/`

- [x] `rsi_strategy.py` - RSIStrategy
  - [x] BUY: RSI < oversold_level (30)
  - [x] SELL: RSI > overbought_level (70)
  - [x] Параметры: rsi_period, oversold, overbought, timeframe
  - [x] ATR для Stop Loss / Take Profit

- [x] `macd_strategy.py` - MACDStrategy
  - [x] BUY: MACD bullish crossover
  - [x] SELL: MACD bearish crossover
  - [x] Параметры: fast_period, slow_period, signal_period, timeframe
  - [x] Confidence на основе histogram

- [x] `multi_tf_strategy.py` - MultiTimeframeStrategy
  - [x] EMA на высоком TF для определения тренда
  - [x] RSI на низком TF для генерации сигналов
  - [x] Фильтрация по тренду
  - [x] Параметры: high_timeframe, low_timeframe, ema_period, rsi_period

- [ ] **Тесты:** `tests/unit/test_strategies.py`
  - [ ] Тест генерации сигналов для каждой стратегии
  - [ ] Использовать фикстуры с историческими данными

### 5.4 API для стратегий ✅

**Файлы:** `backend/app/api/v1/strategies.py`

- [x] `GET /api/v1/strategies/` - список стратегий
  - [x] Возвращает StrategyListResponse

- [x] `GET /api/v1/strategies/{name}` - информация о стратегии
  - [x] Возвращает StrategyInfo

- [x] `GET /api/v1/strategies/{name}/details` - детальная информация
  - [x] Возвращает required_timeframes и indicators_config

- [x] `GET /api/v1/strategies/stats/summary` - статистика

- [x] Обновлён main.py с подключением роутера

- [ ] **Тесты:** integration тесты API endpoints

---

## Фаза 6: Генерация сигналов (2-3 дня)

### 6.1 Генератор сигналов

**Файлы:** `backend/app/signals/generator.py`

- [ ] Класс `SignalGenerator`
  ```python
  class SignalGenerator:
      def __init__(self, strategy: BaseStrategy)

      def generate_signals(self,
                           ticker: str,
                           start_date: date,
                           end_date: date) -> list[Signal]

      def generate_signal_for_point(self,
                                     data: dict[str, pd.DataFrame],
                                     current_idx: int) -> Signal | None
  ```

- [ ] Реализовать пошаговую генерацию сигналов
  - Итерация по историческим данным
  - Вызов стратегии для каждой точки
  - Сохранение сигналов в БД

### 6.2 Риск-менеджмент

**Файлы:** `backend/app/signals/risk_manager.py`

- [ ] Класс `RiskManager`
  ```python
  class RiskManager:
      def __init__(self,
                   max_position_size: float = 0.1,
                   max_daily_signals: int = 5)

      def filter_signals(self, signals: list[Signal]) -> list[Signal]

      def calculate_position_size(self,
                                   signal: Signal,
                                   portfolio_value: float) -> float

      def calculate_stop_loss(self, signal: Signal, atr: float) -> float

      def calculate_take_profit(self, signal: Signal,
                                 risk_reward: float = 2.0) -> float
  ```

- [ ] Реализовать фильтрацию сигналов
  - Ограничение по размеру позиции
  - Ограничение по количеству сигналов в день

### 6.3 Фильтры сигналов

**Файлы:** `backend/app/signals/filters.py`

- [ ] `filter_by_volume(signals, min_volume)` - фильтр по объёму
- [ ] `filter_by_confidence(signals, min_confidence)` - по уверенности
- [ ] `filter_duplicates(signals)` - удаление дубликатов

### 6.4 API для сигналов

**Файлы:** `backend/app/api/v1/signals.py`

- [ ] `GET /api/v1/signals` - история сигналов
  - Query параметры: `ticker`, `start`, `end`, `strategy`

- [ ] `POST /api/v1/signals/generate` - генерация новых сигналов
  - Body: `{strategy_id, tickers: [], start_date, end_date}`
  - Запуск `SignalGenerator`

- [ ] **Тесты:**
  - [ ] Тест генерации сигналов через API
  - [ ] Тест фильтрации по параметрам

---

## Фаза 7: Backtesting Engine (4-5 дней)

### 7.1 Виртуальный портфель

**Файлы:** `backend/app/backtesting/portfolio.py`

- [ ] Класс `Portfolio`
  ```python
  class Portfolio:
      def __init__(self, initial_capital: float)

      cash: float
      positions: dict[str, int]  # {ticker: quantity}
      equity_curve: list[dict]

      def buy(self, ticker, quantity, price) -> bool
      def sell(self, ticker, quantity, price) -> bool
      def get_total_value(self, current_prices: dict) -> float
      def get_position_value(self, ticker, current_price) -> float
  ```

### 7.2 Логика ордеров

**Файлы:** `backend/app/backtesting/order.py`

- [ ] Класс `Order`
  ```python
  class Order:
      order_type: str  # "MARKET", "LIMIT"
      side: str  # "BUY", "SELL"
      ticker: str
      quantity: int
      price: float

      def execute(self, current_price: float) -> bool
  ```

- [ ] Реализовать лимитные ордера
  - Проверка условий исполнения
  - Slippage (опционально)

### 7.3 Движок бэктестинга

**Файлы:** `backend/app/backtesting/engine.py`

- [ ] Класс `BacktestEngine`
  ```python
  class BacktestEngine:
      def __init__(self,
                   strategy: BaseStrategy,
                   initial_capital: float = 100000)

      portfolio: Portfolio
      trades: list[Trade]

      def run(self,
              tickers: list[str],
              start_date: date,
              end_date: date) -> BacktestResult

      def execute_signal(self, signal: Signal, current_price: float) -> None

      def calculate_metrics(self) -> dict
  ```

- [ ] Реализовать основной цикл бэктестинга
  - Загрузка данных для всех таймфреймов
  - Итерация по датам
  - Генерация сигналов
  - Исполнение ордеров
  - Обновление портфеля
  - Запись equity curve

### 7.4 Генератор отчётов

**Файлы:** `backend/app/backtesting/reporter.py`

- [ ] Класс `BacktestReporter`
  ```python
  class BacktestReporter:
      def calculate_metrics(self,
                            portfolio: Portfolio,
                            trades: list[Trade]) -> dict

      # Метрики:
      # - Total Return
      # - Annualized Return
      # - Sharpe Ratio
      # - Max Drawdown
      # - Win Rate
      # - Profit Factor
      # - Total Trades

      def generate_report(self, result: BacktestResult) -> dict
  ```

### 7.5 API для бэктестинга

**Файлы:** `backend/app/api/v1/backtesting.py`

- [ ] `POST /api/v1/backtest/run` - запуск бэктеста
  - Body: `{strategy_id, tickers, start_date, end_date, initial_capital, commission}`
  - Возвращать ID бэктеста

- [ ] `GET /api/v1/backtest/{id}/results` - результаты бэктеста
  - Метрики производительности
  - Equity curve

- [ ] `GET /api/v1/backtest/{id}/trades` - список сделок
  - История всех сделок

- [ ] **Тесты:**
  - [ ] Тест полного цикла бэктестинга
  - [ ] Тест расчёта метрик
  - [ ] Сравнение с ожидаемыми результатами

---

## Фаза 8: Frontend - Основа (3-4 дня)

### 8.1 Структура проекта

- [ ] Создать модульную структуру
  - `core/` - services, interceptors, guards
  - `shared/` - components, pipes, models
  - `features/` - страницы приложения

### 8.2 Core сервисы

**Файлы:** `frontend/src/app/core/services/`

- [ ] `api.service.ts`
  ```typescript
  @Injectable({ providedIn: 'root' })
  export class ApiService {
      getInstruments(): Observable<Instrument[]>
      getInstrument(ticker: string): Observable<Instrument>
      getOHLCV(ticker, timeframe, start, end): Observable<any>
      calculateIndicator(config): Observable<any>
      generateSignals(config): Observable<Signal[]>
      runBacktest(config): Observable<BacktestResult>
  }
  ```

- [ ] `storage.service.ts` - LocalStorage wrapper

- [ ] `websocket.service.ts` (опционально для будущего)

### 8.3 Interceptors

**Файлы:** `frontend/src/app/core/interceptors/`

- [ ] `auth.interceptor.ts`
  - Добавление токена к запросам (для будущей аутентификации)

- [ ] `error.interceptor.ts`
  - Обработка ошибок HTTP
  - Логирование
  - Отображение toast уведомлений

### 8.4 Shared Models

**Файлы:** `frontend/src/app/shared/models/`

- [ ] `instrument.model.ts`
  ```typescript
  export interface Instrument {
      ticker: string;
      name: string;
      market: string;
      instrumentType: string;
      indexId?: number;
  }
  ```

- [ ] `indicator.model.ts`, `signal.model.ts`, `backtest.model.ts`

### 8.5 App Configuration

**Файлы:**

- [ ] `app.config.ts` - ApplicationConfig с providers
- [ ] `app.routes.ts` - маршруты приложения
- [ ] `environments/` - environment конфигурации

### 8.6 Shared Components

**Файлы:** `frontend/src/app/shared/components/`

- [ ] `loader/` - компонент загрузки
- [ ] `error-message/` - отображение ошибок
- [ ] `confirm-dialog/` - диалог подтверждения

---

## Фаза 9: Frontend - Dashboard & Analysis (5-6 дней)

### 9.1 Dashboard

**Файлы:** `frontend/src/app/features/dashboard/`

- [ ] `dashboard.component.ts`
  - [ ] Обзор портфеля (в будущем)
  - [ ] Последние сигналы (топ 5)
  - [ ] Краткая статистика

- [ ] `dashboard.routes.ts`

### 9.2 Analysis Feature

**Файлы:** `frontend/src/app/features/analysis/`

- [ ] `analysis.component.ts` - главный компонент
  - [ ] Layout: селекторы + график + панель индикаторов
  - [ ] State management с Signals
  - [ ] Загрузка данных

- [ ] `components/instrument-selector/`
  - [ ] Dropdown с поиском инструментов
  - [ ] Группировка по типу (stocks, futures, indexes)

- [ ] `components/chart/candlestick-chart.component.ts`
  - [ ] Интеграция ngx-echarts
  - [ ] Отображение candlestick данных
  - [ ] Overlay индикаторов на график
  - [ ] Маркеры сигналов (BUY/SELL)
  - [ ] Zoom & pan
  - [ ] Tooltip с данными

- [ ] `components/indicator-panel/`
  - [ ] Список доступных индикаторов
  - [ ] Конфигурация параметров индикатора
  - [ ] Добавление/удаление индикаторов
  - [ ] Выбор таймфрейма для индикатора

- [ ] `services/analysis.service.ts`
  - [ ] Wrapper над ApiService
  - [ ] State management для Analysis feature

- [ ] **Тесты:**
  - [ ] Unit тесты компонентов
  - [ ] Тесты сервисов с моками

### 9.3 ECharts интеграция

- [ ] Установить `npm install echarts ngx-echarts`
- [ ] Настроить в `angular.json` (assets)
- [ ] Создать конфигурацию для candlestick chart
- [ ] Добавить индикаторы как отдельные series
- [ ] Добавить volume chart (опционально)

---

## Фаза 10: Frontend - Signals & Strategies (3-4 дня)

### 10.1 Signals Feature

**Файлы:** `frontend/src/app/features/signals/`

- [ ] `signals.component.ts`
  - [ ] Таблица сигналов
  - [ ] Фильтры (ticker, dates, strategy, type)
  - [ ] Пагинация

- [ ] `components/signal-list/`
  - [ ] Отображение списка сигналов
  - [ ] Сортировка по колонкам

- [ ] `components/signal-details/`
  - [ ] Детальная информация о сигнале
  - [ ] График с точкой входа

- [ ] `components/signal-filters/`
  - [ ] Форма фильтров
  - [ ] Date range picker

- [ ] `services/signals.service.ts`

### 10.2 Strategies Feature

**Файлы:** `frontend/src/app/features/strategies/`

- [ ] `strategies.component.ts`
  - [ ] Список доступных стратегий
  - [ ] Создание новой стратегии

- [ ] `components/strategy-list/`
  - [ ] Карточки стратегий
  - [ ] Описание, используемые индикаторы

- [ ] `components/strategy-builder/`
  - [ ] Визуальный конструктор стратегии (упрощённый)
  - [ ] Выбор индикаторов с таймфреймами
  - [ ] Настройка правил (entry/exit)

- [ ] `components/strategy-details/`
  - [ ] Детальная информация
  - [ ] История сигналов по стратегии

- [ ] `services/strategies.service.ts`

---

## Фаза 11: Frontend - Backtesting (3-4 дня)

### 11.1 Backtesting Feature

**Файлы:** `frontend/src/app/features/backtesting/`

- [ ] `backtesting.component.ts`
  - [ ] Форма конфигурации бэктеста
  - [ ] Запуск бэктеста
  - [ ] Отображение результатов

- [ ] `components/backtest-config/`
  - [ ] Форма с валидацией
  - [ ] Выбор стратегии
  - [ ] Выбор инструментов
  - [ ] Date range
  - [ ] Initial capital, commission

- [ ] `components/backtest-results/`
  - [ ] Метрики производительности
    - Total Return, Sharpe Ratio, Max Drawdown
    - Win Rate, Profit Factor, Total Trades
  - [ ] Визуализация метрик (карточки, gauges)

- [ ] `components/equity-curve/`
  - [ ] График equity curve (линейный график)
  - [ ] Drawdown график

- [ ] `components/trade-list/`
  - [ ] Таблица всех сделок
  - [ ] Entry/Exit цены, даты
  - [ ] P&L по каждой сделке

- [ ] `services/backtesting.service.ts`

---

## Фаза 12: Frontend - Instruments Management (1-2 дня)

### 12.1 Instruments Feature

**Файлы:** `frontend/src/app/features/instruments/`

- [ ] `instruments.component.ts`
  - [ ] Таблица инструментов
  - [ ] CRUD операции

- [ ] `components/instrument-list/`
  - [ ] Список с фильтрами

- [ ] `components/instrument-form/`
  - [ ] Форма добавления/редактирования
  - [ ] Связывание с индексом

- [ ] `services/instruments.service.ts`
  - [ ] CRUD через ApiService
  - [ ] State management с Signals

---

## Фаза 13: Кэширование и оптимизация (2-3 дня)

### 13.1 Redis кэширование (Backend)

**Файлы:** `backend/app/core/cache.py`

- [ ] Класс `CacheManager`
  ```python
  class CacheManager:
      def get_indicator(ticker, timeframe, indicator_name, params) -> pd.Series
      def set_indicator(ticker, timeframe, indicator_name, params, data) -> None
      def invalidate_ticker(ticker) -> None
  ```

- [ ] Интеграция с расчётом индикаторов
  - Проверка кэша перед расчётом
  - Сохранение результатов в Redis

- [ ] TTL для кэша (например, 1 день)

### 13.2 Оптимизация запросов к БД

- [ ] Проверить индексы на таблице OHLCV
- [ ] Добавить составные индексы если нужно
- [ ] Использовать `select_in_load` для relationships
- [ ] Pagination для больших списков

### 13.3 Frontend оптимизация

- [ ] Lazy loading для feature модулей (уже есть)
- [ ] Debounce на фильтрах (RxJS `debounceTime`)
- [ ] Virtual scrolling для длинных списков (Angular CDK)
- [ ] OnPush change detection где возможно

---

## Фаза 14: Тестирование и документация (3-4 дня)

### 14.1 Backend тестирование

- [ ] Увеличить покрытие unit тестов до >80%
  - [ ] Все модели
  - [ ] Все индикаторы
  - [ ] Все стратегии
  - [ ] Логика бэктестинга

- [ ] Integration тесты для всех API endpoints
  - [ ] Использовать TestClient (FastAPI)
  - [ ] Тестовая БД (SQLite или отдельная PostgreSQL)

- [ ] End-to-end тесты (опционально)
  - [ ] Полный workflow: импорт -> стратегия -> сигналы -> бэктест

- [ ] Запуск тестов: `pytest --cov=app tests/`

### 14.2 Frontend тестирование

- [ ] Unit тесты компонентов
  - [ ] TestBed setup
  - [ ] Тестирование логики компонентов
  - [ ] Моки для сервисов

- [ ] Unit тесты сервисов
  - [ ] HttpClientTestingModule
  - [ ] Тестирование HTTP запросов

- [ ] Запуск тестов: `ng test`

### 14.3 Документация

- [ ] README.md
  - [ ] Описание проекта
  - [ ] Установка и запуск
  - [ ] Структура проекта
  - [ ] Примеры использования

- [ ] API документация
  - [ ] OpenAPI/Swagger для FastAPI
  - [ ] Автоматическая генерация: `/docs`

- [ ] Code documentation
  - [ ] Docstrings для всех классов и методов (Python)
  - [ ] JSDoc для TypeScript (опционально)

- [ ] User Guide
  - [ ] Как добавить индикатор
  - [ ] Как создать стратегию
  - [ ] Как импортировать данные
  - [ ] Как запустить бэктест

---

## Фаза 15: Deployment и DevOps (2-3 дня)

### 15.1 Docker контейнеризация

- [ ] `backend/Dockerfile`
  ```dockerfile
  FROM python:3.11-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install -r requirements.txt
  COPY . .
  CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
  ```

- [ ] `frontend/Dockerfile`
  ```dockerfile
  FROM node:20-alpine AS build
  WORKDIR /app
  COPY package*.json ./
  RUN npm ci
  COPY . .
  RUN npm run build

  FROM nginx:alpine
  COPY --from=build /app/dist/trading-signals-frontend/browser /usr/share/nginx/html
  ```

- [ ] `nginx.conf` для Angular SPA routing

### 15.2 Docker Compose

- [ ] Обновить `docker-compose.yml`
  - [ ] PostgreSQL + TimescaleDB extension
  - [ ] Redis
  - [ ] Backend service
  - [ ] Frontend service (nginx)
  - [ ] Volumes для данных
  - [ ] Networks

### 15.3 Environment конфигурация

- [ ] `.env.example` с переменными окружения
- [ ] Настройка production конфигурации
  - [ ] Backend: production database URL
  - [ ] Frontend: production API URL

### 15.4 CI/CD (опционально)

- [ ] GitHub Actions workflow
  - [ ] Lint и тесты на каждый push
  - [ ] Build Docker images
  - [ ] Deploy (если нужно)

---

## Фаза 16: Расширения и улучшения (опционально)

### 16.1 Дополнительные индикаторы

- [ ] Volume-based индикаторы (OBV, VWAP)
- [ ] Паттерны свечей (Doji, Hammer, etc.)
- [ ] Fibonacci retracements
- [ ] Support/Resistance levels

### 16.2 Продвинутый risk-management

- [ ] Kelly Criterion для размера позиции
- [ ] Trailing Stop Loss
- [ ] Динамическое управление позициями
- [ ] Корреляция между инструментами

### 16.3 Экспорт отчётов

- [ ] PDF отчёты (ReportLab)
- [ ] Excel экспорт (openpyxl)
- [ ] Email отправка отчётов

### 16.4 Real-time данные (будущее)

- [ ] WebSocket для real-time updates
- [ ] Интеграция с биржевыми API (MOEX ISS, Tinkoff)
- [ ] Live сигналы

### 16.5 Machine Learning (будущее)

- [ ] Интеграция scikit-learn
- [ ] Предсказание цен (LSTM, Prophet)
- [ ] Feature engineering из индикаторов
- [ ] Оптимизация параметров стратегий (Grid Search)

---

## Контрольные точки (Checkpoints)

### Checkpoint 1 (после Фазы 2)
- ✅ БД поднята и работает
- ✅ Модели созданы, миграции применены
- ✅ API для инструментов и данных работает
- ✅ Можно импортировать CSV и получать OHLCV через API
- **Критерий:** `GET /api/v1/data/GAZP?timeframe=1h` возвращает данные

### Checkpoint 2 (после Фазы 5)
- ✅ Индикаторы рассчитываются корректно
- ✅ Стратегии генерируют сигналы
- ✅ Multi-timeframe поддержка работает
- **Критерий:** Стратегия с MA(1d) + RSI(1h) генерирует сигналы

### Checkpoint 3 (после Фазы 7)
- ✅ Бэктестинг работает end-to-end
- ✅ Equity curve строится
- ✅ Метрики рассчитываются корректно
- **Критерий:** Бэктест стратегии на GAZP за год возвращает результаты

### Checkpoint 4 (после Фазы 11)
- ✅ Frontend полностью функционален
- ✅ Можно построить график с индикаторами
- ✅ Можно запустить бэктест через UI
- ✅ Результаты визуализируются
- **Критерий:** Пользователь может пройти полный workflow через UI

### Checkpoint 5 (после Фазы 15)
- ✅ Приложение запускается через Docker Compose
- ✅ Все тесты проходят
- ✅ Документация актуальна
- **Критерий:** `docker-compose up` запускает всё приложение

---

## Оценка времени

**Минимальный MVP (Фазы 0-7):** 3-4 недели
**Полный функционал (Фазы 0-12):** 6-8 недель
**С оптимизацией и документацией (Фазы 0-14):** 8-10 недель
**Production-ready (Фазы 0-15):** 10-12 недель

---

## Примечания

1. **Придерживаться SOLID принципов**
   - Single Responsibility: каждый класс = одна ответственность
   - Open/Closed: расширяемость через наследование и декораторы
   - Liskov Substitution: стратегии и индикаторы взаимозаменяемы
   - Interface Segregation: минимальные интерфейсы
   - Dependency Inversion: зависимости через абстракции

2. **Перед каждым коммитом:**
   - Удалить `nul` файлы (из global CLAUDE.md)
   - Прогнать все тесты: `pytest` и `ng test`
   - Исправить failing тесты

3. **Code Review каждой фазы**
   - Проверить соответствие архитектуре
   - Проверить покрытие тестами
   - Проверить документацию

4. **Приоритеты:**
   - Фазы 1-7 (Backend MVP) - критичны
   - Фазы 8-11 (Frontend) - критичны
   - Фазы 13-15 (оптимизация, deployment) - важны
   - Фаза 16 (расширения) - nice to have

---

**Версия:** 1.0
**Дата создания:** 2025-12-01
**Последнее обновление:** 2025-12-01
