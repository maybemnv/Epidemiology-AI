"""
Pytest Configuration and Shared Fixtures

This file configures pytest-asyncio and provides shared fixtures for all tests.
"""

import os
import sys
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure pytest-asyncio
pytest_plugins = ("pytest_asyncio",)


# Test database configuration
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/epidemiology_ai_test",
)

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_async_session_factory = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture
async def db_session():
    """Create a fresh database session for tests."""
    async with test_async_session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client():
    """Create test HTTP client."""
    from src.app import create_app

    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
async def test_user(db_session):
    """Create a test user."""
    from src.database.models import User
    from src.core.security import get_password_hash

    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        first_name="Test",
        last_name="User",
        is_active=True,
        is_superuser=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_admin(db_session):
    """Create a test admin user."""
    from src.database.models import User
    from src.core.security import get_password_hash

    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        first_name="Admin",
        last_name="User",
        is_active=True,
        is_superuser=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_disease(db_session):
    """Create a test disease."""
    from src.database.models import Disease

    disease = Disease(
        name="Dengue",
        description="Mosquito-borne viral disease",
        transmission_type="vector-borne",
        seasonal_pattern="monsoon",
    )
    db_session.add(disease)
    await db_session.commit()
    await db_session.refresh(disease)
    return disease


@pytest.fixture
async def test_region(db_session):
    """Create a test region."""
    from src.database.models import GeographicRegion

    region = GeographicRegion(
        name="San Juan",
        region_type="city",
        latitude=18.4655,
        longitude=-66.1057,
        population=342259,
    )
    db_session.add(region)
    await db_session.commit()
    await db_session.refresh(region)
    return region


@pytest.fixture
async def user_token(test_user):
    """Create a test JWT token."""
    from src.core.security import create_access_token

    return create_access_token(subject=test_user.email)


@pytest.fixture
async def admin_token(test_admin):
    """Create an admin JWT token."""
    from src.core.security import create_access_token

    return create_access_token(subject=test_admin.email)
