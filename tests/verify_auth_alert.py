import sys
import os
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import delete, select
from datetime import datetime
from main import app
from src.database.core import AsyncSessionLocal
from scripts.alert_scheduler import check_alerts
from src.database.models import (
    User,
    Prediction,
    Alert,
    GeographicRegion,
    Disease,
)

sys.path.append(os.getcwd())


async def run_verification():
    print("VERIFYING AUTH AND ALERTS (ASYNC)")

    async with AsyncSessionLocal() as session:
        # Cleanup
        try:
            print("Cleaning up previous test data...")
            await session.execute(delete(Alert))
            await session.execute(delete(Prediction))
            await session.execute(
                delete(User).where(User.email == "test_auth@example.com")
            )
            await session.execute(
                delete(GeographicRegion).where(GeographicRegion.code == "test_reg_auth")
            )
            await session.execute(delete(Disease).where(Disease.name == "Auth Disease"))
            await session.commit()
        except Exception as e:
            print(f"Cleanup warning: {e}")
            await session.rollback()

    # API Client
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Test Register
        print("\n1. Testing Registration...")
        try:
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": "test_auth@example.com",
                    "password": "strongpassword",
                    "full_name": "Auth Tester",
                },
            )
            if response.status_code == 200:
                print("✓ Registration successful")
                data = response.json()
                assert data["email"] == "test_auth@example.com"
            else:
                print(
                    f"✗ Registration failed status "
                    f"{response.status_code}: {response.text}"
                )
        except Exception as e:
            print(f"✗ Registration Exception: {e}")

        # 2. Test Login
        print("\n2. Testing Login...")
        try:
            response = await client.post(
                "/api/v1/auth/login",
                data={
                    "username": "test_auth@example.com",
                    "password": "strongpassword",
                },
            )
            if response.status_code == 200:
                print("✓ Login successful")
                token = response.json()["access_token"]
                print(f"  Token: {token[:10]}...")
            else:
                print(
                    f"✗ Login failed status {response.status_code}: " f"{response.text}"
                )
        except Exception as e:
            print(f"✗ Login Exception: {e}")

    # 3. Test Alert Engine (Direct DB interaction)
    print("\n3. Testing Alert Engine...")
    async with AsyncSessionLocal() as session:
        try:
            # Setup prerequisites
            region = GeographicRegion(
                name="Test Reg Auth",
                code="test_reg_auth",
                country="Test",
                coordinates={},
            )
            disease = Disease(name="Auth Disease", vector="Test")
            session.add(region)
            session.add(disease)
            await session.commit()
            await session.refresh(region)
            await session.refresh(disease)

            # Insert High Risk Prediction
            pred = Prediction(
                prediction_date=datetime.now(),
                predicted_cases=100.0,
                confidence_score=0.9,
                risk_level="High",
                disease_id=disease.id,
                region_id=region.id,
                features_used={},
            )
            session.add(pred)
            await session.commit()

            # Run Scheduler Logic
            print("  Running check_alerts()...")
            await check_alerts()

            # Verify Alert

            result = await session.execute(
                select(Alert).where(Alert.region_id == region.id)
            )
            alert = result.scalars().first()
            if alert:
                print(f"✓ Alert found: {alert.message}")
            else:
                print("✗ Alert NOT found")

            # Final Cleanup
            try:
                if alert:
                    await session.delete(alert)
                await session.delete(pred)
                await session.delete(region)
                await session.delete(disease)
                await session.execute(
                    delete(User).where(User.email == "test_auth@example.com")
                )
                await session.commit()
                print("✓ Cleanup complete")
            except Exception as e:
                print(f"Cleanup Exception: {e}")

        except Exception as e:
            print(f"✗ Alert Engine Exception: {e}")
            await session.rollback()


if __name__ == "__main__":
    asyncio.run(run_verification())
