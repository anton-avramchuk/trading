-- Инициализация TimescaleDB расширения
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Создание схемы для приложения
CREATE SCHEMA IF NOT EXISTS trading;

-- Установка search_path
ALTER DATABASE trading_signals SET search_path TO trading, public;

-- Логирование успешной инициализации
DO $$
BEGIN
    RAISE NOTICE 'TimescaleDB extension initialized successfully';
END $$;
