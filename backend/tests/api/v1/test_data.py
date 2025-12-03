"""
Интеграционные тесты для API endpoints данных
"""
import pytest
from fastapi import status


class TestDataAPI:
    """Тесты для /api/v1/data"""

    def test_get_ohlcv_instrument_not_found(self, client):
        """Тест получения данных для несуществующего инструмента"""
        response = client.get("/api/v1/data/NONEXISTENT?timeframe=1d")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_get_ohlcv_invalid_timeframe(self, client, sample_instrument):
        """Тест получения данных с некорректным таймфреймом"""
        response = client.get(f"/api/v1/data/{sample_instrument.ticker}?timeframe=invalid")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "unsupported timeframe" in response.json()["detail"].lower()

    def test_get_ohlcv_no_data(self, client, sample_instrument):
        """Тест получения пустых данных"""
        response = client.get(f"/api/v1/data/{sample_instrument.ticker}?timeframe=1d")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_ohlcv_with_data(self, client, sample_ohlcv, sample_instrument):
        """Тест получения OHLCV данных"""
        response = client.get(f"/api/v1/data/{sample_instrument.ticker}?timeframe=1d")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 10
        assert "timestamp" in data[0]
        assert "open" in data[0]
        assert "high" in data[0]
        assert "low" in data[0]
        assert "close" in data[0]
        assert "volume" in data[0]

    def test_get_ohlcv_with_limit(self, client, sample_ohlcv, sample_instrument):
        """Тест получения данных с лимитом"""
        response = client.get(f"/api/v1/data/{sample_instrument.ticker}?timeframe=1d&limit=5")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 5

    def test_get_ohlcv_with_date_filter(self, client, sample_ohlcv, sample_instrument):
        """Тест получения данных с фильтром по дате"""
        response = client.get(
            f"/api/v1/data/{sample_instrument.ticker}?"
            f"timeframe=1d&start_date=2024-01-05&end_date=2024-01-07"
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= 3  # Может быть меньше из-за границ дат

    def test_get_supported_timeframes(self, client):
        """Тест получения списка поддерживаемых таймфреймов"""
        response = client.get("/api/v1/data/timeframes/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "timeframes" in data
        assert "descriptions" in data
        assert len(data["timeframes"]) > 0
        assert "1d" in data["timeframes"]
        assert "1h" in data["timeframes"]

    def test_get_latest_ohlcv_not_found(self, client):
        """Тест получения последней свечи для несуществующего инструмента"""
        response = client.get("/api/v1/data/NONEXISTENT/latest?timeframe=1d")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_latest_ohlcv_no_data(self, client, sample_instrument):
        """Тест получения последней свечи при отсутствии данных"""
        response = client.get(f"/api/v1/data/{sample_instrument.ticker}/latest?timeframe=1d")
        assert response.status_code == status.HTTP_200_OK
        # Должен вернуть null/None если данных нет
        assert response.json() is None

    def test_get_latest_ohlcv_with_data(self, client, sample_ohlcv, sample_instrument):
        """Тест получения последней свечи"""
        response = client.get(f"/api/v1/data/{sample_instrument.ticker}/latest?timeframe=1d")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data is not None
        assert "timestamp" in data
        assert "close" in data
        # Проверим, что это действительно последняя свеча
        assert data["close"] == 111.0  # close последней свечи (102.0 + 9)

    def test_get_latest_ohlcv_invalid_timeframe(self, client, sample_instrument):
        """Тест получения последней свечи с некорректным таймфреймом"""
        response = client.get(f"/api/v1/data/{sample_instrument.ticker}/latest?timeframe=invalid")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
