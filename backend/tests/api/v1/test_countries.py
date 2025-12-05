"""
Интеграционные тесты для API endpoints стран
"""
import pytest
from fastapi import status

from app.models.country import Country


class TestCountriesAPI:
    """Тесты для /api/v1/countries"""

    def test_get_countries_empty(self, client):
        """Тест получения пустого списка стран"""
        response = client.get("/api/v1/countries/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_create_country(self, client):
        """Тест создания страны"""
        country_data = {
            "code": "RU",
            "code3": "RUS",
            "name": "Россия",
            "name_en": "Russia",
            "region": "Europe",
            "is_active": 1
        }
        response = client.post("/api/v1/countries/", json=country_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["code"] == "RU"
        assert data["code3"] == "RUS"
        assert data["region"] == "Europe"
        assert "id" in data
        assert "created_at" in data

    def test_create_country_duplicate(self, client, test_db):
        """Тест создания дублирующейся страны"""
        # Создаем первую страну
        country = Country(
            code="US",
            name="США"
        )
        test_db.add(country)
        test_db.commit()

        # Пытаемся создать дубликат
        country_data = {
            "code": "US",
            "name": "United States"
        }
        response = client.post("/api/v1/countries/", json=country_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"].lower()

    def test_get_countries(self, client, test_db):
        """Тест получения списка стран"""
        # Создаем страны
        countries = [
            Country(code="RU", name="Россия", region="Europe"),
            Country(code="US", name="США", region="Americas"),
            Country(code="CN", name="Китай", region="Asia"),
        ]
        for country in countries:
            test_db.add(country)
        test_db.commit()

        response = client.get("/api/v1/countries/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
        assert {c["code"] for c in data} == {"RU", "US", "CN"}

    def test_get_countries_with_pagination(self, client, test_db):
        """Тест пагинации списка стран"""
        for i in range(5):
            country = Country(
                code=f"C{i}",
                name=f"Country {i}"
            )
            test_db.add(country)
        test_db.commit()

        response = client.get("/api/v1/countries/?skip=1&limit=2")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

    def test_get_countries_active_only(self, client, test_db):
        """Тест фильтрации активных стран"""
        countries = [
            Country(code="RU", name="Россия", is_active=1),
            Country(code="US", name="США", is_active=1),
            Country(code="XX", name="Old Country", is_active=0),
        ]
        for country in countries:
            test_db.add(country)
        test_db.commit()

        response = client.get("/api/v1/countries/?active_only=true")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert all(c["is_active"] == 1 for c in data)

    def test_get_countries_by_region(self, client, test_db):
        """Тест фильтрации стран по региону"""
        countries = [
            Country(code="RU", name="Россия", region="Europe"),
            Country(code="DE", name="Германия", region="Europe"),
            Country(code="CN", name="Китай", region="Asia"),
        ]
        for country in countries:
            test_db.add(country)
        test_db.commit()

        response = client.get("/api/v1/countries/?region=Europe")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert all(c["region"] == "Europe" for c in data)

    def test_get_country_by_id(self, client, test_db):
        """Тест получения страны по ID"""
        country = Country(
            code="RU",
            code3="RUS",
            name="Россия",
            region="Europe"
        )
        test_db.add(country)
        test_db.commit()
        test_db.refresh(country)

        response = client.get(f"/api/v1/countries/{country.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["code"] == "RU"
        assert data["code3"] == "RUS"

    def test_get_country_by_id_not_found(self, client):
        """Тест получения несуществующей страны"""
        response = client.get("/api/v1/countries/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_get_country_by_code(self, client, test_db):
        """Тест получения страны по коду"""
        country = Country(
            code="US",
            code3="USA",
            name="США",
            region="Americas"
        )
        test_db.add(country)
        test_db.commit()

        response = client.get("/api/v1/countries/code/US")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["code"] == "US"
        assert data["code3"] == "USA"

    def test_get_country_by_code_case_insensitive(self, client, test_db):
        """Тест поиска страны без учёта регистра"""
        country = Country(code="RU", name="Россия")
        test_db.add(country)
        test_db.commit()

        response = client.get("/api/v1/countries/code/ru")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["code"] == "RU"

    def test_get_country_by_code_not_found(self, client):
        """Тест получения несуществующей страны по коду"""
        response = client.get("/api/v1/countries/code/XX")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_country(self, client, test_db):
        """Тест обновления страны"""
        country = Country(
            code="RU",
            name="Россия",
            region="Asia"
        )
        test_db.add(country)
        test_db.commit()
        test_db.refresh(country)

        update_data = {
            "region": "Europe",
            "name_en": "Russia"
        }
        response = client.patch(f"/api/v1/countries/{country.id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["region"] == "Europe"
        assert data["name_en"] == "Russia"
        assert data["code"] == "RU"  # Код не изменился

    def test_update_country_not_found(self, client):
        """Тест обновления несуществующей страны"""
        update_data = {"region": "Europe"}
        response = client.patch("/api/v1/countries/999", json=update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_country(self, client, test_db):
        """Тест удаления страны"""
        country = Country(code="XX", name="Old Country")
        test_db.add(country)
        test_db.commit()
        test_db.refresh(country)

        response = client.delete(f"/api/v1/countries/{country.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Проверяем, что страна удалена
        response = client.get(f"/api/v1/countries/{country.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_country_not_found(self, client):
        """Тест удаления несуществующей страны"""
        response = client.delete("/api/v1/countries/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
