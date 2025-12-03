"""
Интеграционные тесты для API endpoints бэктестинга
"""
import pytest
from fastapi import status


class TestBacktestingAPI:
    """Тесты для /api/v1/backtest"""

    def test_get_metrics_description(self, client):
        """Тест получения описания метрик"""
        response = client.get("/api/v1/backtest/metrics/description")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Проверяем наличие основных метрик
        assert "total_return" in data
        assert "annualized_return" in data
        assert "total_trades" in data
        assert "win_rate" in data
        assert "profit_factor" in data
        assert "max_drawdown" in data
        assert "sharpe_ratio" in data

        # Проверяем, что описания - строки
        assert isinstance(data["total_return"], str)
        assert isinstance(data["win_rate"], str)
        assert len(data["total_return"]) > 0
