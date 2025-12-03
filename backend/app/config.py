"""
Конфигурация приложения
"""
from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения"""

    # Database
    DATABASE_URL: str = "postgresql://trading_user:trading_password@localhost:5432/trading_signals"

    # Redis
    REDIS_URL: str = "redis://:redis_password@localhost:6379/0"
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 3600  # 1 час

    # API
    API_V1_PREFIX: str = "/api/v1"
    DEBUG_MODE: bool = False

    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:4200",
        "http://localhost:3000",
        "http://localhost:8080"
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Парсинг ALLOWED_ORIGINS из строки с запятыми или JSON"""
        if isinstance(v, str):
            # Попытка распарсить как JSON
            import json
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                pass
            # Если не JSON, то разбиваем по запятым
            return [origin.strip() for origin in v.split(",")]
        return v

    # Logging
    LOG_LEVEL: str = "INFO"

    # Backtesting
    MAX_BACKTEST_DAYS: int = 365
    DEFAULT_INITIAL_CAPITAL: float = 100000.0
    DEFAULT_COMMISSION: float = 0.0005

    # Application
    PROJECT_NAME: str = "Trading Signals"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "Trading signals analysis and backtesting system"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


@lru_cache()
def get_settings() -> Settings:
    """Получить настройки приложения (синглтон)"""
    return Settings()


# Экспорт для удобства
settings = get_settings()
