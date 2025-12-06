"""
Интеграционные тесты для API endpoints стран
"""
import pytest
from fastapi import status

from app.models.country import Country


class TestCountriesAPI:
    """Тесты для /api/v1/countries"""

    def test_get_countries_empty(self, client):
        """Тест получения списка стран (может быть seed data)"""
        response = client.get("/api/v1/countries/")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

    def test_create_country(self, client):
        """Тест создания страны"""
        country_data = {
            "code": "T1",
            "code3": "TST",
            "name": "Тестовая страна",
            "name_en": "Test Country",
            "region": "Europe",
            "is_active": 1
        }
        response = client.post("/api/v1/countries/", json=country_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["code"] == "T1"
        assert data["code3"] == "TST"
        assert data["region"] == "Europe"
        assert "id" in data
        assert "created_at" in data

    def test_create_country_duplicate(self, client, test_db):
        """Тест создания дублирующейся страны"""
        # Создаем первую страну
        country = Country(
            code="T2",
            name="Test Country 2"
        )
        test_db.add(country)
        test_db.commit()

        # Пытаемся создать дубликат
        country_data = {
            "code": "T2",
            "name": "Duplicate Country"
        }
        response = client.post("/api/v1/countries/", json=country_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"].lower()

    def test_get_countries(self, client, test_db):
        """Тест получения списка стран"""
        # Создаем страны
        countries = [
            Country(code="T3", name="Test 3", region="Europe"),
            Country(code="T4", name="Test 4", region="Americas"),
            Country(code="T5", name="Test 5", region="Asia"),
        ]
        for country in countries:
            test_db.add(country)
        test_db.commit()

        response = client.get("/api/v1/countries/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Проверяем что наши тестовые страны есть в списке
        codes = {c["code"] for c in data}
        assert "T3" in codes and "T4" in codes and "T5" in codes

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
            Country(code="T6", name="Test 6", is_active=1),
            Country(code="T7", name="Test 7", is_active=1),
            Country(code="T8", name="Test 8", is_active=0),
        ]
        for country in countries:
            test_db.add(country)
        test_db.commit()

        response = client.get("/api/v1/countries/?active_only=true")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Проверяем что все возвращенные страны активны
        assert all(c["is_active"] == 1 for c in data)
        # Проверяем что наши тестовые активные страны есть
        codes = {c["code"] for c in data}
        assert "T6" in codes and "T7" in codes
        assert "T8" not in codes

    def test_get_countries_by_region(self, client, test_db):
        """Тест фильтрации стран по региону"""
        countries = [
            Country(code="T9", name="Test 9", region="TestRegion"),
            Country(code="TA", name="Test A", region="TestRegion"),
            Country(code="TB", name="Test B", region="OtherRegion"),
        ]
        for country in countries:
            test_db.add(country)
        test_db.commit()

        response = client.get("/api/v1/countries/?region=TestRegion")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Все возвращенные страны должны быть из TestRegion
        assert all(c["region"] == "TestRegion" for c in data)
        codes = {c["code"] for c in data}
        assert "T9" in codes and "TA" in codes
        assert "TB" not in codes

    def test_get_country_by_id(self, client, test_db):
        """Тест получения страны по ID"""
        country = Country(
            code="TC",
            code3="TCC",
            name="Test Country C",
            region="Europe"
        )
        test_db.add(country)
        test_db.commit()
        test_db.refresh(country)

        response = client.get(f"/api/v1/countries/{country.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["code"] == "TC"
        assert data["code3"] == "TCC"

    def test_get_country_by_id_not_found(self, client):
        """Тест получения несуществующей страны"""
        response = client.get("/api/v1/countries/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_get_country_by_code(self, client, test_db):
        """Тест получения страны по коду"""
        country = Country(
            code="TD",
            code3="TDD",
            name="Test Country D",
            region="Americas"
        )
        test_db.add(country)
        test_db.commit()

        response = client.get("/api/v1/countries/code/TD")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["code"] == "TD"
        assert data["code3"] == "TDD"

    def test_get_country_by_code_case_insensitive(self, client, test_db):
        """Тест поиска страны без учёта регистра"""
        country = Country(code="TE", name="Test Country E")
        test_db.add(country)
        test_db.commit()

        response = client.get("/api/v1/countries/code/te")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["code"] == "TE"

    def test_get_country_by_code_not_found(self, client):
        """Тест получения несуществующей страны по коду"""
        response = client.get("/api/v1/countries/code/ZZZ")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_country(self, client, test_db):
        """Тест обновления страны"""
        country = Country(
            code="TF",
            name="Test Country F",
            region="Asia"
        )
        test_db.add(country)
        test_db.commit()
        test_db.refresh(country)

        update_data = {
            "region": "Europe",
            "name_en": "Test F Updated"
        }
        response = client.patch(f"/api/v1/countries/{country.id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["region"] == "Europe"
        assert data["name_en"] == "Test F Updated"
        assert data["code"] == "TF"  # Код не изменился

    def test_update_country_not_found(self, client):
        """Тест обновления несуществующей страны"""
        update_data = {"region": "Europe"}
        response = client.patch("/api/v1/countries/999999", json=update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_country(self, client, test_db):
        """Тест удаления страны"""
        country = Country(code="TG", name="Test Country G")
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
