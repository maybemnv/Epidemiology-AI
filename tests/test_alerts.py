"""
Tests for Alert Management Endpoints

Test CRUD operations for alerts.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import async_sessionmaker

from main import app
from src.database.core import get_db
from src.database.models import Alert, GeographicRegion, User
from src.core import security


# Test database setup
@pytest.fixture
async def db_session():
    """Create a fresh database session for tests"""
    async with async_sessionmaker() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session):
    """Create test client with overridden dependencies"""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_region(db_session):
    """Create a test region"""
    region = GeographicRegion(
        name="Test Region",
        code="test",
        country="Test Country",
        coordinates={"lat": 40.7128, "lon": -74.0060},
        population=1000000,
    )
    db_session.add(region)
    await db_session.commit()
    await db_session.refresh(region)
    return region


@pytest.fixture
async def test_user(db_session):
    """Create a test user"""
    user = User(
        email="user@example.com",
        hashed_password=security.get_password_hash("password123"),
        full_name="Test User",
        is_active=True,
        is_superuser=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_superuser(db_session):
    """Create a test superuser"""
    user = User(
        email="admin@example.com",
        hashed_password=security.get_password_hash("adminpass123"),
        full_name="Admin User",
        is_active=True,
        is_superuser=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_alert(db_session, test_region):
    """Create a test alert"""
    alert = Alert(
        severity="Warning",
        message="Test alert message",
        region_id=test_region.id,
        status="New",
    )
    db_session.add(alert)
    await db_session.commit()
    await db_session.refresh(alert)
    return alert


async def get_access_token(client: AsyncClient, email: str, password: str) -> str:
    """Helper to get access token"""
    response = await client.post(
        "/api/v1/auth/login", data={"username": email, "password": password}
    )
    return response.json()["access_token"]


class TestGetAlerts:
    """Test GET alerts endpoints"""

    async def test_get_all_alerts_empty(self, client: AsyncClient, test_user):
        """Test getting alerts when none exist"""
        token = await get_access_token(client, "user@example.com", "password123")

        response = await client.get(
            "/api/v1/alerts", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json() == []

    async def test_get_all_alerts_with_data(
        self, client: AsyncClient, test_user, test_alert
    ):
        """Test getting alerts with existing data"""
        token = await get_access_token(client, "user@example.com", "password123")

        response = await client.get(
            "/api/v1/alerts", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        alerts = response.json()
        assert len(alerts) == 1
        assert alerts[0]["id"] == test_alert.id
        assert alerts[0]["severity"] == "Warning"
        assert alerts[0]["message"] == "Test alert message"

    async def test_get_alerts_filter_by_status(
        self, client: AsyncClient, test_user, db_session
    ):
        """Test filtering alerts by status"""
        # Create alerts with different statuses
        region = GeographicRegion(name="Region 1", code="r1", country="Country")
        db_session.add(region)
        await db_session.commit()

        for status in ["New", "Acknowledged", "Resolved"]:
            alert = Alert(
                severity="Warning",
                message=f"{status} alert",
                region_id=region.id,
                status=status,
            )
            db_session.add(alert)
        await db_session.commit()

        token = await get_access_token(client, "user@example.com", "password123")

        response = await client.get(
            "/api/v1/alerts?status=New", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        alerts = response.json()
        assert len(alerts) == 1
        assert alerts[0]["status"] == "New"

    async def test_get_alert_by_id(self, client: AsyncClient, test_user, test_alert):
        """Test getting a specific alert by ID"""
        token = await get_access_token(client, "user@example.com", "password123")

        response = await client.get(
            f"/api/v1/alerts/{test_alert.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_alert.id
        assert data["message"] == "Test alert message"

    async def test_get_alert_not_found(self, client: AsyncClient, test_user):
        """Test getting a non-existent alert"""
        token = await get_access_token(client, "user@example.com", "password123")

        response = await client.get(
            "/api/v1/alerts/999", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404


class TestCreateAlert:
    """Test POST alert endpoint"""

    async def test_create_alert_superuser(
        self, client: AsyncClient, test_superuser, test_region
    ):
        """Test creating an alert as superuser"""
        token = await get_access_token(client, "admin@example.com", "adminpass123")

        response = await client.post(
            "/api/v1/alerts",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "severity": "Critical",
                "message": "Critical outbreak detected!",
                "region_id": test_region.id,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["severity"] == "Critical"
        assert data["message"] == "Critical outbreak detected!"
        assert data["status"] == "New"
        assert data["region_id"] == test_region.id

    async def test_create_alert_regular_user_forbidden(
        self, client: AsyncClient, test_user, test_region
    ):
        """Test that regular users cannot create alerts"""
        token = await get_access_token(client, "user@example.com", "password123")

        response = await client.post(
            "/api/v1/alerts",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "severity": "Warning",
                "message": "Test alert",
                "region_id": test_region.id,
            },
        )

        assert response.status_code == 403

    async def test_create_alert_invalid_region(
        self, client: AsyncClient, test_superuser
    ):
        """Test creating alert with invalid region ID"""
        token = await get_access_token(client, "admin@example.com", "adminpass123")

        response = await client.post(
            "/api/v1/alerts",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "severity": "Warning",
                "message": "Test alert",
                "region_id": 999,
            },
        )

        assert response.status_code == 400
        assert "Region" in response.json()["detail"]


class TestUpdateAlert:
    """Test PUT alert endpoint"""

    async def test_update_alert_superuser(
        self, client: AsyncClient, test_superuser, test_alert
    ):
        """Test updating an alert as superuser"""
        token = await get_access_token(client, "admin@example.com", "adminpass123")

        response = await client.put(
            f"/api/v1/alerts/{test_alert.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"severity": "Critical", "message": "Updated message"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["severity"] == "Critical"
        assert data["message"] == "Updated message"

    async def test_update_alert_regular_user_forbidden(
        self, client: AsyncClient, test_user, test_alert
    ):
        """Test that regular users cannot update alerts"""
        token = await get_access_token(client, "user@example.com", "password123")

        response = await client.put(
            f"/api/v1/alerts/{test_alert.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"severity": "Critical"},
        )

        assert response.status_code == 403


class TestAcknowledgeAlert:
    """Test POST alert acknowledge endpoint"""

    async def test_acknowledge_alert(self, client: AsyncClient, test_user, test_alert):
        """Test acknowledging an alert"""
        token = await get_access_token(client, "user@example.com", "password123")

        response = await client.post(
            f"/api/v1/alerts/{test_alert.id}/acknowledge",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Acknowledged"
        assert data["assigned_to_id"] == test_user.id

    async def test_acknowledge_alert_not_found(self, client: AsyncClient, test_user):
        """Test acknowledging non-existent alert"""
        token = await get_access_token(client, "user@example.com", "password123")

        response = await client.post(
            "/api/v1/alerts/999/acknowledge",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404


class TestResolveAlert:
    """Test POST alert resolve endpoint"""

    async def test_resolve_alert_superuser(
        self, client: AsyncClient, test_superuser, test_alert
    ):
        """Test resolving an alert as superuser"""
        token = await get_access_token(client, "admin@example.com", "adminpass123")

        response = await client.post(
            f"/api/v1/alerts/{test_alert.id}/resolve",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Resolved"

    async def test_resolve_alert_regular_user_forbidden(
        self, client: AsyncClient, test_user, test_alert
    ):
        """Test that regular users cannot resolve alerts"""
        token = await get_access_token(client, "user@example.com", "password123")

        response = await client.post(
            f"/api/v1/alerts/{test_alert.id}/resolve",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403


class TestDeleteAlert:
    """Test DELETE alert endpoint"""

    async def test_delete_alert_superuser(
        self, client: AsyncClient, test_superuser, test_alert
    ):
        """Test deleting an alert as superuser"""
        token = await get_access_token(client, "admin@example.com", "adminpass123")

        response = await client.delete(
            f"/api/v1/alerts/{test_alert.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 204

        # Verify alert was deleted
        result = await client.get(
            f"/api/v1/alerts/{test_alert.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert result.status_code == 404

    async def test_delete_alert_regular_user_forbidden(
        self, client: AsyncClient, test_user, test_alert
    ):
        """Test that regular users cannot delete alerts"""
        token = await get_access_token(client, "user@example.com", "password123")

        response = await client.delete(
            f"/api/v1/alerts/{test_alert.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403


class TestAlertsSummary:
    """Test alerts summary endpoint"""

    async def test_get_alerts_summary(self, client: AsyncClient, test_user, db_session):
        """Test getting alerts summary statistics"""
        # Create test data
        region = GeographicRegion(name="Region 1", code="r1", country="Country")
        db_session.add(region)
        await db_session.commit()

        for status in ["New", "New", "Acknowledged", "Resolved"]:
            alert = Alert(
                severity="Warning", message="Test", region_id=region.id, status=status
            )
            db_session.add(alert)

        for severity in ["Critical", "Critical", "Warning"]:
            alert = Alert(
                severity=severity, message="Test", region_id=region.id, status="New"
            )
            db_session.add(alert)
        await db_session.commit()

        token = await get_access_token(client, "user@example.com", "password123")

        response = await client.get(
            "/api/v1/alerts/stats/summary", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "by_status" in data
        assert "by_severity" in data
        assert "new_alerts" in data
        assert "timestamp" in data
