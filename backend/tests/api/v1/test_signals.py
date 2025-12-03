"""
Интеграционные тесты для API endpoints сигналов
"""
import pytest
from fastapi import status


class TestSignalsAPI:
    """Тесты для /api/v1/signals"""

    def test_get_signals_empty(self, client):
        """Тест получения пустого списка сигналов"""
        response = client.get("/api/v1/signals/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_signals(self, client, sample_signals):
        """Тест получения списка сигналов"""
        response = client.get("/api/v1/signals/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 5
        assert "ticker" in data[0]
        assert "strategy_name" in data[0]
        assert "signal_type" in data[0]
        assert "timestamp" in data[0]
        assert "price" in data[0]

    def test_get_signals_with_pagination(self, client, sample_signals):
        """Тест пагинации сигналов"""
        response = client.get("/api/v1/signals/?limit=3&offset=1")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= 3

    def test_get_signals_filter_by_ticker(self, client, sample_signals, sample_instrument):
        """Тест фильтрации сигналов по тикеру"""
        response = client.get(f"/api/v1/signals/?ticker={sample_instrument.ticker}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(signal["ticker"] == sample_instrument.ticker for signal in data)

    def test_get_signals_filter_by_strategy(self, client, sample_signals):
        """Тест фильтрации сигналов по стратегии"""
        response = client.get("/api/v1/signals/?strategy=TestStrategy")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(signal["strategy_name"] == "TestStrategy" for signal in data)

    def test_get_signals_filter_by_type(self, client, sample_signals):
        """Тест фильтрации сигналов по типу"""
        response = client.get("/api/v1/signals/?signal_type=BUY")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(signal["signal_type"] == "BUY" for signal in data)

    def test_get_signals_filter_by_date_range(self, client, sample_signals):
        """Тест фильтрации сигналов по диапазону дат"""
        response = client.get(
            "/api/v1/signals/?start_date=2024-01-01&end_date=2024-01-03"
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= 3

    def test_get_signals_filter_by_confidence(self, client, sample_signals):
        """Тест фильтрации сигналов по уверенности"""
        response = client.get("/api/v1/signals/?min_confidence=0.75")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(
            signal["confidence"] is None or signal["confidence"] >= 0.75
            for signal in data
        )

    def test_get_signal_by_id(self, client, sample_signal):
        """Тест получения сигнала по ID"""
        response = client.get(f"/api/v1/signals/{sample_signal.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_signal.id
        assert data["signal_type"] == sample_signal.signal_type
        assert data["price"] == sample_signal.price

    def test_get_signal_not_found(self, client):
        """Тест получения несуществующего сигнала"""
        response = client.get("/api/v1/signals/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_get_signal_stats_empty(self, client):
        """Тест получения статистики при отсутствии сигналов"""
        response = client.get("/api/v1/signals/stats")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_signals"] == 0
        assert data["buy_signals"] == 0
        assert data["sell_signals"] == 0

    def test_get_signal_stats(self, client, sample_signals):
        """Тест получения статистики по сигналам"""
        response = client.get("/api/v1/signals/stats")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_signals" in data
        assert "buy_signals" in data
        assert "sell_signals" in data
        assert "unique_strategies" in data
        assert "unique_instruments" in data
        assert "avg_confidence" in data
        assert "date_range" in data
        assert data["total_signals"] == 5
        assert data["buy_signals"] == 3  # 0, 2, 4 индексы
        assert data["sell_signals"] == 2  # 1, 3 индексы

    def test_get_signal_stats_with_filters(self, client, sample_signals, sample_instrument):
        """Тест получения статистики с фильтрами"""
        response = client.get(
            f"/api/v1/signals/stats?ticker={sample_instrument.ticker}&signal_type=BUY"
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_signals"] == 3
        assert data["sell_signals"] == 0
