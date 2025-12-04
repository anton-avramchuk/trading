"""
Configuration settings for IMOEX service
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # Service
    SERVICE_NAME: str = "imoex"
    SERVICE_PORT: int = 8001
    SERVICE_HOST: str = "0.0.0.0"
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str

    # MOEX API
    MOEX_BASE_URL: str = "https://iss.moex.com/iss"
    MOEX_RATE_LIMIT: int = 10  # requests per second
    MOEX_TIMEOUT: int = 30  # seconds
    MOEX_MAX_RETRIES: int = 3

    # Redis
    REDIS_URL: str
    CACHE_TTL: int = 3600  # seconds

    # Scheduler
    ENABLE_SCHEDULER: bool = False
    UPDATE_SCHEDULE: str = "0 19 * * 1-5"  # Cron: 19:00 on weekdays
    UPDATE_TIMEFRAMES: str = "1d,1h"
    UPDATE_DAYS_BACK: int = 3

    @property
    def update_timeframes_list(self) -> List[str]:
        """Get list of timeframes for updates"""
        return [tf.strip() for tf in self.UPDATE_TIMEFRAMES.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
