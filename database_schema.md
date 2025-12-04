# 🗄️ Схема базы данных Trading Signals

## Обзор

База данных PostgreSQL с поддержкой TimescaleDB для эффективной работы с временными рядами.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DATABASE: trading (PostgreSQL)                        │
└─────────────────────────────────────────────────────────────────────────┘
```

## 📊 ER-диаграмма

```
                    ┌──────────────────────┐
                    │     timeframes       │
                    ├──────────────────────┤
                    │ id (PK)              │
                    │ code (UQ)            │◄────────┐
                    │ name                 │         │
                    │ minutes              │         │
                    │ moex_interval        │         │
                    └──────────────────────┘         │
                                                     │
                                                     │ (1:N)
┌──────────────────────────┐                        │
│       indexes            │                        │
├──────────────────────────┤                        │
│ id (PK)         INTEGER  │                        │
│ name            VARCHAR  │◄──────┐                │
│ ticker (UQ)     VARCHAR  │       │                │
│ description     VARCHAR  │       │ (1:N)          │
│ created_at      DATETIME │       │                │
│ updated_at      DATETIME │       │                │
└──────────────────────────┘       │                │
                                   │                │
┌──────────────────────────────────┼────────────────┼───────────────────┐
│       instruments                │                │                   │
├──────────────────────────────────┤                │                   │
│ id (PK)            INTEGER       │                │                   │
│ ticker (UQ, IDX)   VARCHAR(20)   │                │                   │
│ name               VARCHAR(255)  │                │                   │
│ market             VARCHAR(50)   │ MOEX, CME     │                   │
│ instrument_type    VARCHAR(50)   │ stock, future │                   │
│ index_id (FK, IDX) INTEGER       ├────────────────┘                   │
│ created_at         DATETIME      │                                    │
│ updated_at         DATETIME      │                                    │
└──────────┬───────────────────────┘                                    │
           │                                                             │
           │ (1:N)                                                       │
           │                                                             │
           ├──────────────────────────────────┬──────────────────────────┘
           │                                  │
           │                                  │
    ┌──────▼──────────────────────┐   ┌──────▼─────────────────────┐
    │       ohlcv                 │   │    download_log            │
    ├─────────────────────────────┤   ├────────────────────────────┤
    │ id (PK)          INTEGER    │   │ id (PK)       INTEGER      │
    │ instrument_id (FK, IDX)     │   │ instrument_id (FK, IDX)    │
    │ timeframe_id (FK, IDX) ─────┼───┤ timeframe_id (FK, IDX)     │
    │ timeframe (IDX)  VARCHAR(10)│   │ ticker (IDX)  VARCHAR(20)  │
    │ timestamp (IDX)  DATETIME   │   │ timeframe     VARCHAR(10)  │
    │ open             FLOAT      │   │ market        VARCHAR(50)  │
    │ high             FLOAT      │   │ board         VARCHAR(50)  │
    │ low              FLOAT      │   │ status (IDX)  VARCHAR(20)  │
    │ close            FLOAT      │   │ records_imported INTEGER   │
    │ volume           BIGINT     │   │ start_date    DATETIME     │
    │                             │   │ end_date      DATETIME     │
    │ UNIQUE (instrument_id,      │   │ started_at (IDX) DATETIME  │
    │         timeframe_id,       │   │ completed_at  DATETIME     │
    │         timestamp)          │   │ duration_seconds FLOAT     │
    │ INDEX (instrument_id,       │   │ error         TEXT         │
    │        timeframe_id,        │   │ metadata      JSON         │
    │        timestamp)           │   │ created_at    DATETIME     │
    └─────────────────────────────┘   └────────────────────────────┘

           │ (1:N)
           │
    ┌──────▼─────────────────────┐
    │       signals              │
    ├────────────────────────────┤
    │ id (PK)       INTEGER      │
    │ instrument_id (FK, IDX) ───┘
    │ strategy_id (FK, IDX)      ──┐
    │ strategy_name (IDX)        │ │
    │ signal_type   VARCHAR(10)  │ │
    │ timestamp (IDX) DATETIME   │ │
    │ price         FLOAT        │ │
    │ confidence    FLOAT        │ │
    │ position_size FLOAT        │ │
    │ stop_loss     FLOAT        │ │
    │ take_profit   FLOAT        │ │
    │ created_at    DATETIME     │ │
    └────────────────────────────┘ │
                                   │
                            ┌──────▼──────────────────────┐
                            │       strategies            │
                            ├─────────────────────────────┤
                            │ id (PK)          INTEGER    │
                            │ name (UQ, IDX)   VARCHAR(255)│
                            │ description      TEXT       │
                            │ config           JSON       │
                            │ created_at       DATETIME   │
                            │ updated_at       DATETIME   │
                            │ is_active        INTEGER    │
                            └─────────────────────────────┘
```

## 📋 Детальное описание таблиц

### 1. **timeframes** (Таймфреймы)

Справочник допустимых таймфреймов.

| Колонка       | Тип          | Описание                          | Constraints        |
|---------------|--------------|-----------------------------------|--------------------|
| id            | INTEGER      | Первичный ключ                    | PRIMARY KEY, INDEX |
| code          | VARCHAR(10)  | Код таймфрейма (1m, 10m, 1h, 1d) | UNIQUE, INDEX      |
| name          | VARCHAR(50)  | Название (1 минута, 1 день)       | NOT NULL           |
| description   | TEXT         | Описание                          | NULLABLE           |
| minutes       | INTEGER      | Количество минут                  | NOT NULL, INDEX    |
| moex_interval | INTEGER      | Интервал MOEX API                 | NOT NULL           |
| created_at    | DATETIME     | Дата создания                     |                    |
| is_active     | INTEGER      | Активность (1/0)                  | DEFAULT 1          |

**Начальные данные:**
```sql
INSERT INTO timeframes VALUES
(1, '1m',  '1 минута',   'Минутный таймфрейм',       1,     1,   NOW(), 1),
(2, '10m', '10 минут',   '10-минутный таймфрейм',    10,    10,  NOW(), 1),
(3, '1h',  '1 час',      'Часовой таймфрейм',        60,    60,  NOW(), 1),
(4, '1d',  '1 день',     'Дневной таймфрейм',        1440,  24,  NOW(), 1),
(5, '1w',  '1 неделя',   'Недельный таймфрейм',      10080, 7,   NOW(), 1),
(6, '1M',  '1 месяц',    'Месячный таймфрейм',       43200, 31,  NOW(), 1),
(7, '1Q',  '1 квартал',  'Квартальный таймфрейм',    129600,4,   NOW(), 1);
```

### 2. **indexes** (Биржевые индексы)

Хранит индексы (IMOEX, RTS, S&P500 и т.д.).

| Колонка     | Тип           | Описание            | Constraints        |
|-------------|---------------|---------------------|--------------------|
| id          | INTEGER       | Первичный ключ      | PRIMARY KEY, INDEX |
| name        | VARCHAR(255)  | Название            | NOT NULL           |
| ticker      | VARCHAR(20)   | Тикер (IMOEX)       | UNIQUE, INDEX      |
| description | VARCHAR(1000) | Описание            | NULLABLE           |
| created_at  | DATETIME      | Дата создания       |                    |
| updated_at  | DATETIME      | Дата обновления     |                    |

**Relationships:**
- → instruments (1:N)

### 3. **instruments** (Финансовые инструменты)

Центральная таблица для всех тикеров.

| Колонка         | Тип          | Описание                    | Constraints                   |
|-----------------|--------------|-----------------------------|------------------------------ |
| id              | INTEGER      | Первичный ключ              | PRIMARY KEY, INDEX             |
| ticker          | VARCHAR(20)  | Тикер (GAZP, SBER)          | UNIQUE, INDEX                  |
| name            | VARCHAR(255) | Полное название             | NOT NULL                       |
| market          | VARCHAR(50)  | Биржа (MOEX, CME)           | NOT NULL                       |
| instrument_type | VARCHAR(50)  | Тип (stock, future, index)  | NOT NULL                       |
| index_id        | INTEGER      | ID индекса                  | FK → indexes.id, SET NULL, INDEX|
| created_at      | DATETIME     | Дата создания               |                                |
| updated_at      | DATETIME     | Дата обновления             |                                |

**Relationships:**
- instruments.index_id → indexes.id (N:1)
- → ohlcv (1:N, CASCADE)
- → signals (1:N, CASCADE)
- → download_log (1:N, SET NULL)

### 4. **ohlcv** (Свечные данные)

Исторические OHLCV данные для всех инструментов.

| Колонка        | Тип         | Описание                 | Constraints                       |
|----------------|-------------|--------------------------|-----------------------------------|
| id             | INTEGER     | Первичный ключ           | PRIMARY KEY, INDEX                |
| instrument_id  | INTEGER     | ID инструмента           | FK → instruments.id, CASCADE, INDEX|
| timeframe_id   | INTEGER     | ID таймфрейма            | FK → timeframes.id, INDEX          |
| timeframe      | VARCHAR(10) | Код таймфрейма           | NOT NULL, INDEX                    |
| timestamp      | DATETIME    | Временная метка          | NOT NULL, INDEX                    |
| open           | FLOAT       | Цена открытия            | NOT NULL                           |
| high           | FLOAT       | Максимальная цена        | NOT NULL                           |
| low            | FLOAT       | Минимальная цена         | NOT NULL                           |
| close          | FLOAT       | Цена закрытия            | NOT NULL                           |
| volume         | BIGINT      | Объём торгов             | NOT NULL                           |

**Constraints:**
```sql
UNIQUE (instrument_id, timeframe_id, timestamp)
INDEX (instrument_id, timeframe_id, timestamp)  -- Composite index
```

**Relationships:**
- ohlcv.instrument_id → instruments.id (N:1, CASCADE)
- ohlcv.timeframe_id → timeframes.id (N:1)

**Валидация:**
- `high >= max(open, close)`
- `low <= min(open, close)`
- Все цены > 0

### 5. **signals** (Торговые сигналы)

Сигналы, сгенерированные стратегиями.

| Колонка       | Тип          | Описание                    | Constraints                      |
|---------------|--------------|-----------------------------| ---------------------------------|
| id            | INTEGER      | Первичный ключ              | PRIMARY KEY, INDEX                |
| instrument_id | INTEGER      | ID инструмента              | FK → instruments.id, CASCADE, INDEX|
| strategy_id   | INTEGER      | ID стратегии                | FK → strategies.id, SET NULL, INDEX|
| strategy_name | VARCHAR(255) | Название стратегии          | NOT NULL, INDEX                   |
| signal_type   | VARCHAR(10)  | Тип (BUY/SELL)              | NOT NULL                          |
| timestamp     | DATETIME     | Время сигнала               | NOT NULL, INDEX                   |
| price         | FLOAT        | Цена                        | NOT NULL                          |
| confidence    | FLOAT        | Уверенность (0-1)           | NULLABLE                          |
| position_size | FLOAT        | Размер позиции              | NULLABLE                          |
| stop_loss     | FLOAT        | Стоп-лосс                   | NULLABLE                          |
| take_profit   | FLOAT        | Тейк-профит                 | NULLABLE                          |
| created_at    | DATETIME     | Дата создания               |                                   |

**Relationships:**
- signals.instrument_id → instruments.id (N:1, CASCADE)
- signals.strategy_id → strategies.id (N:1, SET NULL)

### 6. **strategies** (Торговые стратегии)

Конфигурация торговых стратегий.

| Колонка     | Тип          | Описание                 | Constraints        |
|-------------|--------------|--------------------------|-------------------|
| id          | INTEGER      | Первичный ключ           | PRIMARY KEY, INDEX |
| name        | VARCHAR(255) | Название стратегии       | UNIQUE, INDEX      |
| description | TEXT         | Описание                 | NULLABLE           |
| config      | JSON         | Конфигурация в JSON      | NOT NULL           |
| created_at  | DATETIME     | Дата создания            |                    |
| updated_at  | DATETIME     | Дата обновления          |                    |
| is_active   | INTEGER      | Активность (1/0)         | DEFAULT 1          |

**JSON config пример:**
```json
{
  "indicators": [
    {"name": "MA", "timeframe": "1d", "params": {"period": 50}},
    {"name": "RSI", "timeframe": "1h", "params": {"period": 14}}
  ],
  "rules": {
    "entry": "close > MA_1d AND RSI_1h < 30",
    "exit": "RSI_1h > 70"
  },
  "risk_management": {
    "stop_loss_atr_multiplier": 2.0,
    "take_profit_atr_multiplier": 3.0,
    "max_position_size": 0.05
  }
}
```

**Relationships:**
- → signals (1:N)

### 7. **download_log** (Логи загрузок MOEX)

Отслеживание загрузок данных с MOEX ISS API (для IMOEX микросервиса).

| Колонка           | Тип         | Описание                      | Constraints                        |
|-------------------|-------------|-------------------------------|------------------------------------|
| id                | INTEGER     | Первичный ключ                | PRIMARY KEY, INDEX                 |
| instrument_id     | INTEGER     | ID инструмента                | FK → instruments.id, SET NULL, INDEX|
| timeframe_id      | INTEGER     | ID таймфрейма                 | FK → timeframes.id, INDEX          |
| ticker            | VARCHAR(20) | Тикер (для ссылки)            | NOT NULL, INDEX                    |
| timeframe         | VARCHAR(10) | Код таймфрейма                | NOT NULL                           |
| market            | VARCHAR(50) | Рынок (stock, futures)        | NOT NULL                           |
| board             | VARCHAR(50) | Режим торгов (TQBR, RFUD)     | NOT NULL                           |
| status            | VARCHAR(20) | Статус загрузки               | NOT NULL, INDEX                    |
| records_imported  | INTEGER     | Количество загруженных записей| DEFAULT 0                          |
| start_date        | DATETIME    | Начало периода                | NULLABLE                           |
| end_date          | DATETIME    | Конец периода                 | NULLABLE                           |
| started_at        | DATETIME    | Время начала                  | NOT NULL, INDEX                    |
| completed_at      | DATETIME    | Время завершения              | NULLABLE                           |
| duration_seconds  | FLOAT       | Длительность в секундах       | NULLABLE                           |
| error             | TEXT        | Текст ошибки                  | NULLABLE                           |
| metadata          | JSON        | Дополнительная информация     | NULLABLE                           |
| created_at        | DATETIME    | Дата создания записи          |                                    |

**Возможные значения status:**
- `pending` - в очереди
- `running` - выполняется
- `completed` - завершено успешно
- `failed` - ошибка

**JSON metadata пример:**
```json
{
  "pages_fetched": 5,
  "duplicates_skipped": 10,
  "moex_response_time_ms": 1200,
  "validation_errors": [],
  "api_calls": 5,
  "batch_size": 500
}
```

**Relationships:**
- download_log.instrument_id → instruments.id (N:1, SET NULL)
- download_log.timeframe_id → timeframes.id (N:1)

## 🔗 Связи (Foreign Keys)

| From Table     | Column        | To Table    | Column | On Delete  |
|----------------|---------------|-------------|--------|------------|
| instruments    | index_id      | indexes     | id     | SET NULL   |
| ohlcv          | instrument_id | instruments | id     | CASCADE    |
| ohlcv          | timeframe_id  | timeframes  | id     | RESTRICT   |
| signals        | instrument_id | instruments | id     | CASCADE    |
| signals        | strategy_id   | strategies  | id     | SET NULL   |
| download_log   | instrument_id | instruments | id     | SET NULL   |
| download_log   | timeframe_id  | timeframes  | id     | RESTRICT   |

**Правила удаления:**
- `CASCADE` - каскадное удаление (при удалении инструмента удаляются его ohlcv и signals)
- `SET NULL` - установка NULL (при удалении индекса/стратегии FK становится NULL)
- `RESTRICT` - запрет удаления (нельзя удалить timeframe если есть связанные записи)

## 📈 Индексы для производительности

```sql
-- timeframes
CREATE INDEX idx_timeframes_code ON timeframes(code);
CREATE INDEX idx_timeframes_minutes ON timeframes(minutes);

-- indexes
CREATE INDEX idx_indexes_ticker ON indexes(ticker);

-- instruments
CREATE INDEX idx_instruments_ticker ON instruments(ticker);
CREATE INDEX idx_instruments_index ON instruments(index_id);

-- ohlcv
CREATE INDEX idx_ohlcv_instrument ON ohlcv(instrument_id);
CREATE INDEX idx_ohlcv_timeframe_id ON ohlcv(timeframe_id);
CREATE INDEX idx_ohlcv_timeframe ON ohlcv(timeframe);
CREATE INDEX idx_ohlcv_timestamp ON ohlcv(timestamp);
CREATE INDEX idx_ohlcv_composite ON ohlcv(instrument_id, timeframe_id, timestamp);

-- signals
CREATE INDEX idx_signals_instrument ON signals(instrument_id);
CREATE INDEX idx_signals_strategy_id ON signals(strategy_id);
CREATE INDEX idx_signals_strategy_name ON signals(strategy_name);
CREATE INDEX idx_signals_timestamp ON signals(timestamp);

-- strategies
CREATE INDEX idx_strategies_name ON strategies(name);

-- download_log
CREATE INDEX idx_download_log_instrument ON download_log(instrument_id);
CREATE INDEX idx_download_log_timeframe_id ON download_log(timeframe_id);
CREATE INDEX idx_download_log_ticker ON download_log(ticker);
CREATE INDEX idx_download_log_status ON download_log(status);
CREATE INDEX idx_download_log_started ON download_log(started_at);
```

## 🎯 TimescaleDB оптимизация

### Конвертация ohlcv в hypertable:

```sql
-- Конвертация таблицы в hypertable TimescaleDB
SELECT create_hypertable('ohlcv', 'timestamp',
    chunk_time_interval => INTERVAL '1 month',
    if_not_exists => TRUE
);

-- Добавление compression policy
ALTER TABLE ohlcv SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'instrument_id, timeframe_id'
);

-- Автоматическое сжатие данных старше 3 месяцев
SELECT add_compression_policy('ohlcv', INTERVAL '3 months');

-- Retention policy: удаление данных старше 5 лет
SELECT add_retention_policy('ohlcv', INTERVAL '5 years');
```

## 💡 Примеры запросов

### Получить свечи для инструмента:

```sql
SELECT
    o.timestamp,
    o.open,
    o.high,
    o.low,
    o.close,
    o.volume,
    t.code as timeframe
FROM ohlcv o
JOIN instruments i ON o.instrument_id = i.id
JOIN timeframes t ON o.timeframe_id = t.id
WHERE i.ticker = 'GAZP'
  AND t.code = '1d'
  AND o.timestamp >= '2024-01-01'
ORDER BY o.timestamp DESC
LIMIT 100;
```

### Получить последние сигналы по стратегии:

```sql
SELECT
    s.timestamp,
    i.ticker,
    s.signal_type,
    s.price,
    s.confidence,
    st.name as strategy_name
FROM signals s
JOIN instruments i ON s.instrument_id = i.id
JOIN strategies st ON s.strategy_id = st.id
WHERE st.name = 'MACDStrategy'
  AND s.timestamp >= NOW() - INTERVAL '7 days'
ORDER BY s.timestamp DESC;
```

### Статистика загрузок:

```sql
SELECT
    ticker,
    timeframe,
    status,
    COUNT(*) as attempts,
    SUM(records_imported) as total_records,
    AVG(duration_seconds) as avg_duration,
    MAX(completed_at) as last_download
FROM download_log
WHERE started_at >= NOW() - INTERVAL '30 days'
GROUP BY ticker, timeframe, status
ORDER BY total_records DESC;
```

## 🔄 Миграции

### Применение миграций:

```bash
# Применить все миграции
alembic upgrade head

# Откатить последнюю миграцию
alembic downgrade -1

# Посмотреть текущую версию
alembic current

# История миграций
alembic history
```

### Список миграций:

1. `001_initial_schema.py` - Базовые таблицы (instruments, ohlcv, signals)
2. `002_add_strategies.py` - Таблица strategies
3. `003_add_timeframes_and_fks.py` - Таблица timeframes и внешние ключи
4. `004_add_download_log.py` - Таблица download_log для IMOEX

## 📊 Размеры и метрики

### Приблизительные оценки:

| Таблица       | Записей (пример) | Размер (ориентировочно) |
|---------------|------------------|-------------------------|
| timeframes    | 7                | < 1 KB                  |
| indexes       | 10-50            | < 100 KB                |
| instruments   | 100-1000         | 100 KB - 1 MB           |
| ohlcv (1d)    | 250K - 2.5M      | 50 MB - 500 MB          |
| ohlcv (1h)    | 6M - 60M         | 1 GB - 10 GB            |
| signals       | 10K - 100K       | 5 MB - 50 MB            |
| strategies    | 10-100           | < 1 MB                  |
| download_log  | 1K - 10K         | 1 MB - 10 MB            |

**Итого:** 1-20 GB для полного набора данных (зависит от количества инструментов и истории).

## 🛠️ Обслуживание

### Регулярные задачи:

1. **Vacuum** - еженедельно
   ```sql
   VACUUM ANALYZE ohlcv;
   ```

2. **Reindex** - ежемесячно
   ```sql
   REINDEX TABLE ohlcv;
   ```

3. **Статистика** - автоматически
   ```sql
   ANALYZE ohlcv;
   ```

4. **Backup** - ежедневно
   ```bash
   pg_dump -U user -d trading > backup_$(date +%Y%m%d).sql
   ```

## 🔐 Безопасность

### Рекомендации:

1. Использовать разные пользователи БД для разных сервисов
2. Ограничить доступ IMOEX микросервиса только к необходимым таблицам
3. Шифрование соединений (SSL/TLS)
4. Regular password rotation
5. Audit logging для критичных операций

```sql
-- Создание пользователя для IMOEX
CREATE USER imoex_service WITH PASSWORD 'secure_password';

-- Права доступа
GRANT SELECT, INSERT, UPDATE ON instruments TO imoex_service;
GRANT SELECT, INSERT, UPDATE ON ohlcv TO imoex_service;
GRANT SELECT ON timeframes TO imoex_service;
GRANT SELECT, INSERT, UPDATE ON download_log TO imoex_service;
```
