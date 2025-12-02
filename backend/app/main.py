"""
Основное FastAPI приложение
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import settings

# Создание FastAPI приложения
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    debug=settings.DEBUG_MODE
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Действия при запуске приложения"""
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG_MODE}")
    logger.info(f"API prefix: {settings.API_V1_PREFIX}")


@app.on_event("shutdown")
async def shutdown_event():
    """Действия при остановке приложения"""
    logger.info(f"Shutting down {settings.PROJECT_NAME}")


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
from app.api.v1 import data, indicators, instruments, strategies

# Импорт индикаторов и стратегий для автоматической регистрации
import app.indicators  # noqa: F401
import app.strategies  # noqa: F401

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

# Роутеры, которые будут добавлены позже:
# from app.api.v1 import signals, backtesting
# app.include_router(signals.router, prefix=f"{settings.API_V1_PREFIX}/signals", tags=["signals"])
# app.include_router(backtesting.router, prefix=f"{settings.API_V1_PREFIX}/backtest", tags=["backtesting"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG_MODE
    )
