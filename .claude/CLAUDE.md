# Инструкции для проекта Trading Signals

## 📋 Обзор проекта

**Система торговых сигналов** - анализ исторических данных российского фондового рынка и товарных фьючерсов с генерацией торговых сигналов и бэктестингом.

## 🛠 Технологический стек

**Backend:**
- Python 3.11+ / FastAPI
- PostgreSQL (TimescaleDB) + Redis (кэш)
- SQLAlchemy, Alembic, Pydantic
- Pandas/Polars, NumPy, TA-Lib/Pandas-TA

**Frontend:**
- Angular 17+ (standalone компоненты)
- TypeScript, RxJS, Angular Signals
- ngx-echarts (Apache ECharts)
- Angular Material или PrimeNG

## 📁 Структура проекта

```
trading-signals/
├── backend/
│   └── app/
│       ├── core/          # Загрузка данных, timeframe manager
│       ├── models/        # SQLAlchemy модели (instrument, ohlcv, signal)
│       ├── indicators/    # Базовый класс + technical/custom
│       ├── signals/       # Генератор сигналов, риск-менеджмент
│       ├── strategies/    # Базовый класс + примеры
│       ├── backtesting/   # Движок бэктестинга
│       ├── api/v1/        # REST endpoints
│       └── schemas/       # Pydantic схемы
├── frontend/
│   └── src/app/
│       ├── core/          # services, interceptors, guards
│       ├── shared/        # components, pipes, models
│       └── features/      # dashboard, analysis, signals, backtesting
└── data/                  # CSV файлы (moex, futures, indexes)
```

## 🔑 Ключевые концепции

### 1. Multi-Timeframe поддержка
- Индикаторы имеют параметр `timeframe: str`
- `TimeframeManager` выравнивает данные разных таймфреймов
- Стратегии получают `data: dict[str, pd.DataFrame]` с данными всех таймфреймов

### 2. Расширяемая система индикаторов
```python
@register_indicator
class MyIndicator(BaseIndicator):
    name = "MyIndicator"
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        ...
```

### 3. Система стратегий
```python
@register_strategy
class MyStrategy(BaseStrategy):
    def generate_signal(self, data: dict[str, pd.DataFrame]) -> Signal | None:
        ...
```

### 4. Связывание тикеров с индексами
- Модель `Instrument` имеет `index_id` (ForeignKey)
- Позволяет анализировать инструменты в контексте рыночных индексов

## 📡 API Структура

```
/api/v1/instruments     # CRUD инструментов
/api/v1/data           # OHLCV данные
/api/v1/indicators     # Список и расчёт индикаторов
/api/v1/strategies     # CRUD стратегий
/api/v1/signals        # Генерация и история сигналов
/api/v1/backtest       # Запуск и результаты бэктестов
```

## 🎯 Правила разработки

### Backend:
1. **Всегда использовать декораторы** `@register_indicator` и `@register_strategy`
2. **Валидация данных** через Pydantic схемы
3. **Индикаторы кэшируются** - учитывать при разработке
4. **OHLCV индексы**: `(instrument_id, timeframe, timestamp)`
5. **CSV импорт** с валидацией (OHLC корректность, дубликаты)

### Frontend:
1. **Standalone компоненты** (Angular 17+)
2. **Angular Signals** для state management
3. **Lazy loading** для feature модулей
4. **Interceptors**: auth.interceptor, error.interceptor
5. **Маршруты**: используть `loadComponent` и `loadChildren`

## 🔄 Типичные workflow

### Добавление нового индикатора:
1. Создать класс в `backend/app/indicators/custom/`
2. Наследовать `BaseIndicator` + декоратор `@register_indicator`
3. Реализовать `calculate()` метод
4. Автоматически появится в API и UI

### Создание стратегии:
1. Создать класс в `backend/app/strategies/examples/`
2. Наследовать `BaseStrategy` + декоратор `@register_strategy`
3. Определить индикаторы с таймфреймами
4. Реализовать `generate_signal(data: dict[str, pd.DataFrame])`

### Миграция CSV в БД:
```python
from app.utils.csv_importer import CSVImporter
importer = CSVImporter()
importer.import_file(csv_path="data/moex/GAZP_1h.csv", ticker="GAZP", timeframe="1h")
```

## ⚡ Оптимизация

- **Кэширование** индикаторов в Redis
- **Векторизация** расчётов (NumPy)
- **Индексы БД** на (instrument_id, timeframe, timestamp)
- **TimescaleDB** партиционирование по времени
- **Frontend**: виртуализация списков, lazy loading, debounce

## 🚀 Запуск

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

# Docker
docker-compose up
```

## 📊 Модели данных

### Instrument
- ticker (String, unique, index)
- name (String)
- market (String) - "MOEX", "CME" и т.д.
- instrument_type (String) - "stock", "future", "index"
- index_id (Integer, ForeignKey) - связь с индексом

### OHLCV
- instrument_id (Integer, ForeignKey, index)
- timeframe (String, index) - "1h", "1d", "1w", "1M"
- timestamp (DateTime, index)
- open, high, low, close (Float)
- volume (BigInteger)
- Unique: (instrument_id, timeframe, timestamp)

### Signal
- instrument_id (Integer, ForeignKey)
- strategy_name (String)
- signal_type (String) - "BUY", "SELL"
- timestamp (DateTime)
- price (Float)
- confidence (Float, nullable)
- position_size (Float, nullable)
- stop_loss (Float, nullable)
- take_profit (Float, nullable)

### Index
- name (String)
- ticker (String, unique)
- instruments (Relationship)

## 🔐 Безопасность

- Pydantic валидация всех входных данных
- Rate limiting на API
- CORS настройки
- Логирование операций
- Backup БД

## 📝 Дополнительные заметки

- CSV формат: `date,open,high,low,close,volume`
- При импорте проверяется корректность OHLC: H >= max(O,C), L <= min(O,C)
- Поддержка multi-timeframe: индикаторы из разных таймфреймов в одной стратегии
- Бэктестинг с виртуальным портфелем и лимитными ордерами
