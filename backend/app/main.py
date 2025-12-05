"""
Основное FastAPI приложение
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager для startup/shutdown событий"""
    # Startup
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG_MODE}")
    logger.info(f"API prefix: {settings.API_V1_PREFIX}")

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.PROJECT_NAME}")


# Создание FastAPI приложения
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    debug=settings.DEBUG_MODE,
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": settings.DESCRIPTION
    }


@app.get("/health")
async def health_check():
    """Health check эндпоинт"""
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }


# Подключение роутеров
from app.api.v1 import (
    backtesting,
    countries,
    currencies,
    data,
    indicators,
    instruments,
    signals,
    strategies,
)

# Импорт индикаторов и стратегий для автоматической регистрации
from app import indicators as indicators_pkg  # noqa: F401
from app import strategies as strategies_pkg  # noqa: F401

app.include_router(
    currencies.router,
    prefix=f"{settings.API_V1_PREFIX}/currencies",
    tags=["currencies"]
)
app.include_router(
    countries.router,
    prefix=f"{settings.API_V1_PREFIX}/countries",
    tags=["countries"]
)
app.include_router(
    instruments.router,
    prefix=f"{settings.API_V1_PREFIX}/instruments",
    tags=["instruments"]
)
app.include_router(
    data.router,
    prefix=f"{settings.API_V1_PREFIX}/data",
    tags=["data"]
)
app.include_router(
    indicators.router,
    prefix=f"{settings.API_V1_PREFIX}/indicators",
    tags=["indicators"]
)
app.include_router(
    strategies.router,
    prefix=f"{settings.API_V1_PREFIX}/strategies",
    tags=["strategies"]
)
app.include_router(
    signals.router,
    prefix=f"{settings.API_V1_PREFIX}/signals",
    tags=["signals"]
)
app.include_router(
    backtesting.router,
    prefix=f"{settings.API_V1_PREFIX}/backtest",
    tags=["backtesting"]
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG_MODE
    )
