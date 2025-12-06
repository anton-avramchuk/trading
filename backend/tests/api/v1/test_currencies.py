"""
Интеграционные тесты для API endpoints валют
"""
import pytest
from fastapi import status

from app.models.currency import Currency


class TestCurrenciesAPI:
    """Тесты для /api/v1/currencies"""

    def test_get_currencies_empty(self, client):
        """Тест получения списка валют (может быть seed data)"""
        response = client.get("/api/v1/currencies/")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

    def test_create_currency(self, client):
        """Тест создания валюты"""
        currency_data = {
            "code": "TST",
            "numeric_code": "999",
            "name": "Тестовая валюта",
            "name_en": "Test Currency",
            "symbol": "T",
            "decimal_places": 2,
            "is_active": 1
        }
        response = client.post("/api/v1/currencies/", json=currency_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["code"] == "TST"
        assert data["symbol"] == "T"
        assert data["decimal_places"] == 2
        assert "id" in data
        assert "created_at" in data

    def test_create_currency_duplicate(self, client, test_db):
        """Тест создания дублирующейся валюты"""
        # Создаем первую валюту
        currency = Currency(
            code="TC1",
            name="Test Currency 1",
            decimal_places=2
        )
        test_db.add(currency)
        test_db.commit()

        # Пытаемся создать дубликат
        currency_data = {
            "code": "TC1",
            "name": "Duplicate Currency",
            "decimal_places": 2
        }
        response = client.post("/api/v1/currencies/", json=currency_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"].lower()

    def test_get_currencies(self, client, test_db):
        """Тест получения списка валют"""
        # Создаем валюты
        currencies = [
            Currency(code="TC2", name="Test Currency 2", symbol="T2", decimal_places=2),
            Currency(code="TC3", name="Test Currency 3", symbol="T3", decimal_places=2),
            Currency(code="TC4", name="Test Currency 4", symbol="T4", decimal_places=2),
        ]
        for currency in currencies:
            test_db.add(currency)
        test_db.commit()

        response = client.get("/api/v1/currencies/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Проверяем что наши тестовые валюты есть в списке
        codes = {c["code"] for c in data}
        assert "TC2" in codes and "TC3" in codes and "TC4" in codes

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
            Currency(code="TC5", name="Test Currency 5", is_active=1, decimal_places=2),
            Currency(code="TC6", name="Test Currency 6", is_active=1, decimal_places=2),
            Currency(code="TC7", name="Test Currency 7", is_active=0, decimal_places=2),
        ]
        for currency in currencies:
            test_db.add(currency)
        test_db.commit()

        response = client.get("/api/v1/currencies/?active_only=true")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Все возвращенные валюты должны быть активны
        assert all(c["is_active"] == 1 for c in data)
        codes = {c["code"] for c in data}
        assert "TC5" in codes and "TC6" in codes
        assert "TC7" not in codes

    def test_get_currency_by_id(self, client, test_db):
        """Тест получения валюты по ID"""
        currency = Currency(
            code="TC8",
            name="Test Currency 8",
            symbol="T8",
            decimal_places=2
        )
        test_db.add(currency)
        test_db.commit()
        test_db.refresh(currency)

        response = client.get(f"/api/v1/currencies/{currency.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["code"] == "TC8"
        assert data["symbol"] == "T8"

    def test_get_currency_by_id_not_found(self, client):
        """Тест получения несуществующей валюты"""
        response = client.get("/api/v1/currencies/999999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_get_currency_by_code(self, client, test_db):
        """Тест получения валюты по коду"""
        currency = Currency(
            code="TC9",
            name="Test Currency 9",
            symbol="T9",
            decimal_places=2
        )
        test_db.add(currency)
        test_db.commit()

        response = client.get("/api/v1/currencies/code/TC9")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["code"] == "TC9"
        assert data["symbol"] == "T9"

    def test_get_currency_by_code_case_insensitive(self, client, test_db):
        """Тест поиска валюты без учёта регистра"""
        currency = Currency(code="TCA", name="Test Currency A", decimal_places=2)
        test_db.add(currency)
        test_db.commit()

        response = client.get("/api/v1/currencies/code/tca")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["code"] == "TCA"

    def test_get_currency_by_code_not_found(self, client):
        """Тест получения несуществующей валюты по коду"""
        response = client.get("/api/v1/currencies/code/ZZZ")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_currency(self, client, test_db):
        """Тест обновления валюты"""
        currency = Currency(
            code="TCB",
            name="Test Currency B",
            symbol="р",
            decimal_places=2
        )
        test_db.add(currency)
        test_db.commit()
        test_db.refresh(currency)

        update_data = {
            "symbol": "TB",
            "name": "Test Currency B Updated"
        }
        response = client.patch(f"/api/v1/currencies/{currency.id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["symbol"] == "TB"
        assert data["name"] == "Test Currency B Updated"
        assert data["code"] == "TCB"  # Код не изменился

    def test_update_currency_not_found(self, client):
        """Тест обновления несуществующей валюты"""
        update_data = {"symbol": "$"}
        response = client.patch("/api/v1/currencies/999999", json=update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_currency(self, client, test_db):
        """Тест удаления валюты"""
        currency = Currency(code="TCC", name="Test Currency C", decimal_places=2)
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
        response = client.delete("/api/v1/currencies/999999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_crypto_currency(self, client):
        """Тест создания криптовалюты с длинным кодом"""
        currency_data = {
            "code": "TCRYPTO",
            "name": "Test Crypto Currency",
            "symbol": "TC",
            "decimal_places": 8,
            "is_active": 1
        }
        response = client.post("/api/v1/currencies/", json=currency_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["code"] == "TCRYPTO"
        assert data["decimal_places"] == 8
