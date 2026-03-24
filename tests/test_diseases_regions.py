"""
Tests for Disease and Region API endpoints.
"""

import pytest
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession


class TestDiseaseEndpoints:
    @pytest.mark.asyncio
    async def test_list_diseases_empty(self, client, db_session):
        response = await client.get("/api/v1/diseases")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"] == []
        assert data["pagination"]["total"] == 0

    @pytest.mark.asyncio
    async def test_create_disease(self, client, admin_token):
        disease_data = {
            "name": "Dengue",
            "description": "Mosquito-borne viral disease",
            "transmission_type": "vector-borne",
            "seasonal_pattern": "monsoon",
        }
        response = await client.post(
            "/api/v1/diseases",
            json=disease_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Dengue"
        assert data["transmission_type"] == "vector-borne"

    @pytest.mark.asyncio
    async def test_create_disease_duplicate(self, client, admin_token, test_disease):
        disease_data = {
            "name": test_disease.name,
            "description": "Duplicate disease",
        }
        response = await client.post(
            "/api/v1/diseases",
            json=disease_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_get_disease(self, client, test_disease):
        response = await client.get(f"/api/v1/diseases/{test_disease.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_disease.id
        assert data["name"] == test_disease.name

    @pytest.mark.asyncio
    async def test_get_disease_not_found(self, client):
        response = await client.get("/api/v1/diseases/9999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_disease(self, client, admin_token, test_disease):
        update_data = {"description": "Updated description"}
        response = await client.put(
            f"/api/v1/diseases/{test_disease.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == "Updated description"

    @pytest.mark.asyncio
    async def test_delete_disease(self, client, admin_token, test_disease, db_session):
        response = await client.delete(
            f"/api/v1/diseases/{test_disease.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        db: AsyncSession = db_session
        from src.database.models import Disease

        disease = await db.get(Disease, test_disease.id)
        assert disease is None


class TestRegionEndpoints:
    @pytest.mark.asyncio
    async def test_list_regions_empty(self, client):
        response = await client.get("/api/v1/regions")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"] == []

    @pytest.mark.asyncio
    async def test_create_region(self, client, admin_token):
        region_data = {
            "name": "San Juan",
            "region_type": "city",
            "latitude": 18.4655,
            "longitude": -66.1057,
            "population": 342259,
        }
        response = await client.post(
            "/api/v1/regions",
            json=region_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "San Juan"
        assert data["latitude"] == 18.4655

    @pytest.mark.asyncio
    async def test_get_region(self, client, test_region):
        response = await client.get(f"/api/v1/regions/{test_region.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_region.id
        assert data["name"] == test_region.name

    @pytest.mark.asyncio
    async def test_get_region_stats(self, client, test_region):
        response = await client.get(f"/api/v1/regions/{test_region.id}/stats")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["region_id"] == test_region.id
        assert data["region_name"] == test_region.name

    @pytest.mark.asyncio
    async def test_filter_regions_by_type(self, client, test_region):
        response = await client.get("/api/v1/regions?region_type=city")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) >= 1
