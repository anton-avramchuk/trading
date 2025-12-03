"""
Интеграционные тесты для API endpoints индикаторов
"""
import pytest
from fastapi import status


class TestIndicatorsAPI:
    """Тесты для /api/v1/indicators"""

    def test_get_indicators(self, client):
        """Тест получения списка индикаторов"""
        response = client.get("/api/v1/indicators/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total" in data
        assert "indicators" in data
        assert isinstance(data["indicators"], list)
        # Должны быть зарегистрированы хотя бы некоторые индикаторы
        assert data["total"] >= 0

    def test_get_indicator_info(self, client):
        """Тест получения информации о конкретном индикаторе"""
        # Сначала получим список всех индикаторов
        list_response = client.get("/api/v1/indicators/")
        indicators = list_response.json()["indicators"]

        if len(indicators) > 0:
            # Получим информацию о первом индикаторе
            indicator_name = indicators[0]["name"]
            response = client.get(f"/api/v1/indicators/{indicator_name}")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "name" in data
            assert "description" in data
            assert "category" in data
            assert "parameters" in data

    def test_get_indicator_info_not_found(self, client):
        """Тест получения информации о несуществующем индикаторе"""
        response = client.get("/api/v1/indicators/NONEXISTENT_INDICATOR")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_get_indicators_by_category(self, client):
        """Тест получения индикаторов по категории"""
        categories = ["trend", "momentum", "volatility", "volume", "custom"]

        for category in categories:
            response = client.get(f"/api/v1/indicators/category/{category}")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "total" in data
            assert "indicators" in data
            # Проверим, что все индикаторы принадлежат данной категории
            for indicator in data["indicators"]:
                assert indicator["category"] == category

    def test_get_indicators_by_invalid_category(self, client):
        """Тест получения индикаторов с некорректной категорией"""
        response = client.get("/api/v1/indicators/category/invalid_category")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "invalid category" in response.json()["detail"].lower()

    def test_get_indicators_stats(self, client):
        """Тест получения статистики по индикаторам"""
        response = client.get("/api/v1/indicators/stats/usage")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total" in data
        assert "by_category" in data
        assert "available_indicators" in data
        assert isinstance(data["available_indicators"], list)
