"""
Интеграционные тесты для API endpoints стратегий
"""
import pytest
from fastapi import status


class TestStrategiesAPI:
    """Тесты для /api/v1/strategies"""

    def test_get_strategies(self, client):
        """Тест получения списка стратегий"""
        response = client.get("/api/v1/strategies/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total" in data
        assert "strategies" in data
        assert isinstance(data["strategies"], list)
        # Должны быть зарегистрированы хотя бы некоторые стратегии
        assert data["total"] >= 0

    def test_get_strategy_info(self, client):
        """Тест получения информации о конкретной стратегии"""
        # Сначала получим список всех стратегий
        list_response = client.get("/api/v1/strategies/")
        strategies = list_response.json()["strategies"]

        if len(strategies) > 0:
            # Получим информацию о первой стратегии
            strategy_name = strategies[0]["name"]
            response = client.get(f"/api/v1/strategies/{strategy_name}")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "name" in data
            assert "description" in data
            assert "version" in data

    def test_get_strategy_info_not_found(self, client):
        """Тест получения информации о несуществующей стратегии"""
        response = client.get("/api/v1/strategies/NONEXISTENT_STRATEGY")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_get_strategy_details(self, client):
        """Тест получения детальной информации о стратегии"""
        # Получим список стратегий
        list_response = client.get("/api/v1/strategies/")
        strategies = list_response.json()["strategies"]

        if len(strategies) > 0:
            strategy_name = strategies[0]["name"]
            response = client.get(f"/api/v1/strategies/{strategy_name}/details")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "name" in data
            assert "description" in data
            assert "version" in data
            assert "required_timeframes" in data
            assert "indicators_config" in data
            assert isinstance(data["required_timeframes"], list)
            assert isinstance(data["indicators_config"], list)

    def test_get_strategy_details_not_found(self, client):
        """Тест получения деталей несуществующей стратегии"""
        response = client.get("/api/v1/strategies/NONEXISTENT/details")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_strategies_stats(self, client):
        """Тест получения статистики по стратегиям"""
        response = client.get("/api/v1/strategies/stats/summary")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total" in data
        assert "available_strategies" in data
        assert isinstance(data["available_strategies"], list)
