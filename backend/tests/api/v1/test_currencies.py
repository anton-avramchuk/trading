"""
Интеграционные тесты для API endpoints валют
"""
import pytest
from fastapi import status

from app.models.currency import Currency


class TestCurrenciesAPI:
    """Тесты для /api/v1/currencies"""

    def test_get_currencies_empty(self, client):
        """Тест получения пустого списка валют"""
        response = client.get("/api/v1/currencies/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_create_currency(self, client):
        """Тест создания валюты"""
        currency_data = {
            "code": "RUB",
            "numeric_code": "643",
            "name": "Российский рубль",
            "name_en": "Russian Ruble",
            "symbol": "₽",
            "decimal_places": 2,
            "is_active": 1
        }
        response = client.post("/api/v1/currencies/", json=currency_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["code"] == "RUB"
        assert data["symbol"] == "₽"
        assert data["decimal_places"] == 2
        assert "id" in data
        assert "created_at" in data

    def test_create_currency_duplicate(self, client, test_db):
        """Тест создания дублирующейся валюты"""
        # Создаем первую валюту
        currency = Currency(
            code="USD",
            name="Доллар США",
            decimal_places=2
        )
        test_db.add(currency)
        test_db.commit()

        # Пытаемся создать дубликат
        currency_data = {
            "code": "USD",
            "name": "US Dollar",
            "decimal_places": 2
        }
        response = client.post("/api/v1/currencies/", json=currency_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"].lower()

    def test_get_currencies(self, client, test_db):
        """Тест получения списка валют"""
        # Создаем валюты
        currencies = [
            Currency(code="RUB", name="Российский рубль", symbol="₽", decimal_places=2),
            Currency(code="USD", name="Доллар США", symbol="$", decimal_places=2),
            Currency(code="EUR", name="Евро", symbol="€", decimal_places=2),
        ]
        for currency in currencies:
            test_db.add(currency)
        test_db.commit()

        response = client.get("/api/v1/currencies/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
        assert {c["code"] for c in data} == {"RUB", "USD", "EUR"}

    def test_get_currencies_with_pagination(self, client, test_db):
        """Тест пагинации списка валют"""
        for i in range(5):
            currency = Currency(
                code=f"CUR{i}",
                name=f"Currency {i}",
                decimal_places=2
            )
            test_db.add(currency)
        test_db.commit()

        response = client.get("/api/v1/currencies/?skip=1&limit=2")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

    def test_get_currencies_active_only(self, client, test_db):
        """Тест фильтрации активных валют"""
        currencies = [
            Currency(code="RUB", name="Российский рубль", is_active=1, decimal_places=2),
            Currency(code="USD", name="Доллар США", is_active=1, decimal_places=2),
            Currency(code="OLD", name="Old Currency", is_active=0, decimal_places=2),
        ]
        for currency in currencies:
            test_db.add(currency)
        test_db.commit()

        response = client.get("/api/v1/currencies/?active_only=true")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert all(c["is_active"] == 1 for c in data)

    def test_get_currency_by_id(self, client, test_db):
        """Тест получения валюты по ID"""
        currency = Currency(
            code="RUB",
            name="Российский рубль",
            symbol="₽",
            decimal_places=2
        )
        test_db.add(currency)
        test_db.commit()
        test_db.refresh(currency)

        response = client.get(f"/api/v1/currencies/{currency.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["code"] == "RUB"
        assert data["symbol"] == "₽"

    def test_get_currency_by_id_not_found(self, client):
        """Тест получения несуществующей валюты"""
        response = client.get("/api/v1/currencies/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_get_currency_by_code(self, client, test_db):
        """Тест получения валюты по коду"""
        currency = Currency(
            code="USD",
            name="Доллар США",
            symbol="$",
            decimal_places=2
        )
        test_db.add(currency)
        test_db.commit()

        response = client.get("/api/v1/currencies/code/USD")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["code"] == "USD"
        assert data["symbol"] == "$"

    def test_get_currency_by_code_case_insensitive(self, client, test_db):
        """Тест поиска валюты без учёта регистра"""
        currency = Currency(code="RUB", name="Рубль", decimal_places=2)
        test_db.add(currency)
        test_db.commit()

        response = client.get("/api/v1/currencies/code/rub")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["code"] == "RUB"

    def test_get_currency_by_code_not_found(self, client):
        """Тест получения несуществующей валюты по коду"""
        response = client.get("/api/v1/currencies/code/XXX")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_currency(self, client, test_db):
        """Тест обновления валюты"""
        currency = Currency(
            code="RUB",
            name="Рубль",
            symbol="р",
            decimal_places=2
        )
        test_db.add(currency)
        test_db.commit()
        test_db.refresh(currency)

        update_data = {
            "symbol": "₽",
            "name": "Российский рубль"
        }
        response = client.patch(f"/api/v1/currencies/{currency.id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["symbol"] == "₽"
        assert data["name"] == "Российский рубль"
        assert data["code"] == "RUB"  # Код не изменился

    def test_update_currency_not_found(self, client):
        """Тест обновления несуществующей валюты"""
        update_data = {"symbol": "$"}
        response = client.patch("/api/v1/currencies/999", json=update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_currency(self, client, test_db):
        """Тест удаления валюты"""
        currency = Currency(code="OLD", name="Old Currency", decimal_places=2)
        test_db.add(currency)
        test_db.commit()
        test_db.refresh(currency)

        response = client.delete(f"/api/v1/currencies/{currency.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Проверяем, что валюта удалена
        response = client.get(f"/api/v1/currencies/{currency.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_currency_not_found(self, client):
        """Тест удаления несуществующей валюты"""
        response = client.delete("/api/v1/currencies/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_crypto_currency(self, client):
        """Тест создания криптовалюты с длинным кодом"""
        currency_data = {
            "code": "USDT",
            "name": "Tether",
            "symbol": "₮",
            "decimal_places": 8,
            "is_active": 1
        }
        response = client.post("/api/v1/currencies/", json=currency_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["code"] == "USDT"
        assert data["decimal_places"] == 8
