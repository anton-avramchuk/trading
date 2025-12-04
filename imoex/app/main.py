"""
IMOEX Microservice - Main application

This service provides API for downloading historical data from Moscow Exchange (MOEX).
It validates all timeframes against the database to ensure data integrity.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.v1 import health, timeframes, instruments, download
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info(f"Starting {settings.SERVICE_NAME} service...")
    logger.info(f"Database: {settings.DATABASE_URL.split('@')[-1]}")  # Hide credentials
    logger.info(f"MOEX API: {settings.MOEX_BASE_URL}")
    logger.info(f"Rate limit: {settings.MOEX_RATE_LIMIT} req/s")

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.SERVICE_NAME} service...")


# Create FastAPI app
app = FastAPI(
    title="IMOEX Service",
    description="Microservice for downloading historical data from Moscow Exchange",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(timeframes.router, prefix="/api/v1")
app.include_router(instruments.router, prefix="/api/v1")
app.include_router(download.router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.SERVICE_HOST,
        port=settings.SERVICE_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower(),
    )
