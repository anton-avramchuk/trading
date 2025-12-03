"""
Интеграционные тесты для API endpoints инструментов
"""
import pytest
from fastapi import status


class TestInstrumentsAPI:
    """Тесты для /api/v1/instruments"""

    def test_get_instruments_empty(self, client):
        """Тест получения пустого списка инструментов"""
        response = client.get("/api/v1/instruments/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_instruments(self, client, sample_instruments):
        """Тест получения списка инструментов"""
        response = client.get("/api/v1/instruments/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
        assert data[0]["ticker"] in ["GAZP", "SBER", "YNDX"]

    def test_get_instruments_with_pagination(self, client, sample_instruments):
        """Тест пагинации списка инструментов"""
        response = client.get("/api/v1/instruments/?skip=1&limit=2")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

    def test_get_instruments_filter_by_market(self, client, sample_instruments):
        """Тест фильтрации по рынку"""
        response = client.get("/api/v1/instruments/?market=MOEX")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
        assert all(item["market"] == "MOEX" for item in data)

    def test_get_instruments_filter_by_type(self, client, sample_instruments):
        """Тест фильтрации по типу инструмента"""
        response = client.get("/api/v1/instruments/?instrument_type=stock")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
        assert all(item["instrument_type"] == "stock" for item in data)

    def test_get_instrument_by_ticker(self, client, sample_instrument):
        """Тест получения инструмента по тикеру"""
        response = client.get(f"/api/v1/instruments/{sample_instrument.ticker}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["ticker"] == sample_instrument.ticker
        assert data["name"] == sample_instrument.name
        assert "index_name" in data
        assert "index_ticker" in data

    def test_get_instrument_not_found(self, client):
        """Тест получения несуществующего инструмента"""
        response = client.get("/api/v1/instruments/NONEXISTENT")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_get_instrument_case_insensitive(self, client, sample_instrument):
        """Тест поиска инструмента без учёта регистра"""
        response = client.get(f"/api/v1/instruments/{sample_instrument.ticker.lower()}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["ticker"] == sample_instrument.ticker


class TestIndexesAPI:
    """Тесты для /api/v1/instruments/indexes"""

    def test_get_indexes_empty(self, client):
        """Тест получения пустого списка индексов"""
        response = client.get("/api/v1/instruments/indexes/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_indexes(self, client, sample_index):
        """Тест получения списка индексов"""
        response = client.get("/api/v1/instruments/indexes/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["ticker"] == sample_index.ticker
        assert data[0]["name"] == sample_index.name

    def test_get_indexes_with_pagination(self, client, sample_index):
        """Тест пагинации списка индексов"""
        # Создать ещё один индекс
        from app.models.index import Index
        index2 = Index(name="Index 2", ticker="IDX2")
        # Используем test_db из фикстуры client
        # Но у нас нет прямого доступа, поэтому этот тест требует доработки
        pass

    def test_get_index_by_id(self, client, sample_index):
        """Тест получения индекса по ID"""
        response = client.get(f"/api/v1/instruments/indexes/{sample_index.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_index.id
        assert data["ticker"] == sample_index.ticker
        assert data["name"] == sample_index.name

    def test_get_index_not_found(self, client):
        """Тест получения несуществующего индекса"""
        response = client.get("/api/v1/instruments/indexes/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
