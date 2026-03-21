"""
Pytest Configuration and Shared Fixtures

This file configures pytest-asyncio and provides shared fixtures for all tests.
"""

import os
import sys
from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure pytest-asyncio
pytest_plugins = ("pytest_asyncio",)


def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line("markers", "asyncio: mark test as an asyncio test.")


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
    """
    Create a fresh database session for tests.

    Each test gets a fresh session that is rolled back after the test.
    """
    async with test_async_session_factory() as session:
        yield session
        await session.rollback()
