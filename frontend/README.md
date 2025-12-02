# Trading Signals Frontend

Angular 20 приложение для визуализации торговых сигналов и бэктестинга.

## Технологии

- **Angular 20** - фреймворк
- **TypeScript 5.8** - строгая типизация
- **SCSS** - стили
- **ngx-echarts** - графики и charts
- **Angular Material** - UI компоненты
- **RxJS** - реактивное программирование
- **Standalone Components** - новая архитектура Angular

## Структура проекта

```
src/app/
├── core/                  # Singleton сервисы и глобальная логика
│   ├── services/         # API сервисы, auth, state
│   ├── interceptors/     # HTTP interceptors
│   ├── guards/           # Route guards
│   └── models/           # Глобальные интерфейсы и типы
│
├── shared/               # Переиспользуемые компоненты
│   ├── components/       # UI компоненты (buttons, cards, etc.)
│   ├── pipes/            # Custom pipes
│   ├── directives/       # Custom directives
│   └── models/           # Shared интерфейсы
│
└── features/             # Feature модули
    ├── dashboard/        # Главная панель
    ├── instruments/      # Управление инструментами
    ├── indicators/       # Индикаторы
    ├── strategies/       # Стратегии
    ├── signals/          # Торговые сигналы
    └── backtesting/      # Бэктестинг
```

## Установка

```bash
npm install
```

## Запуск

```bash
# Development server
npm start
# или
ng serve

# Production build
npm run build
# или
ng build --configuration production
```

Приложение будет доступно по адресу: http://localhost:4200

## API Backend

Backend API: http://localhost:8000/api/v1

Настройка URL в `src/environments/environment.ts`

## Environments

- **environment.development.ts** - Development окружение
- **environment.ts** - Production окружение

## Стиль кода

- **Strict TypeScript** - включен strict mode
- **Standalone Components** - без NgModules
- **SCSS** - препроцессор стилей

## Features (Roadmap)

### Dashboard
- Общая статистика
- Equity curves
- Последние сигналы

### Instruments
- Список инструментов
- Импорт CSV данных
- OHLCV графики

### Indicators
- Список доступных индикаторов
- Расчёт индикаторов
- Визуализация на графиках

### Strategies
- Список стратегий
- Конфигурация параметров
- Генерация сигналов

### Signals
- История торговых сигналов
- Фильтрация и поиск
- Детали сигнала (SL/TP)

### Backtesting
- Запуск бэктестов
- Метрики производительности
- Сравнение стратегий
- Equity curves
- Trade history

## Разработка

### Создание компонента

```bash
ng generate component features/dashboard/components/equity-chart --standalone
```

### Создание сервиса

```bash
ng generate service core/services/api
```

### Создание guard

```bash
ng generate guard core/guards/auth
```

## Testing

```bash
# Unit tests
npm test
```

## Lint

Angular CLI автоматически проверяет код при сборке.

## Build

```bash
# Development
ng build

# Production
ng build --configuration production
```
