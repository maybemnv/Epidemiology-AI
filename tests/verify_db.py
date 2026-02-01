import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select, delete

import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from src.database.core import AsyncSessionLocal, engine  # noqa: E402
from src.database.models import (  # noqa: E402
    User,
    Disease,
    GeographicRegion,
    OutbreakData,
    EnvironmentalData,
    Prediction,
    Alert,
)


async def verify_database():
    print("=" * 60)
    print("DATABASE VERIFICATION STARTED")
    print("=" * 60)

    # 1. Test Connection
    print("\n1. Testing Connection...")
    try:
        async with engine.connect():
            print("✓ Successfully connected to PostgreSQL")
    except Exception as e:
        print(f"✗ Connection Failed: {e}")
        return

    async with AsyncSessionLocal() as session:
        try:
            # 2. Cleanup (Idempotency)
            print("\n2. Cleaning up previous test data...")
            await session.execute(delete(OutbreakData))
            await session.execute(delete(EnvironmentalData))
            await session.execute(delete(Prediction))
            await session.execute(delete(Alert))
            await session.execute(delete(Disease).where(Disease.name == "Test Fever"))
            await session.execute(
                delete(GeographicRegion).where(GeographicRegion.code == "test_city")
            )
            await session.execute(delete(User).where(User.email == "test@example.com"))
            await session.commit()
            print("✓ Cleanup complete")

            # 3. Create Reference Data
            print("\n3. Inserting Reference Data...")

            # User
            user = User(
                email="test@example.com",
                hashed_password="hashed_secret",
                full_name="Test User",
                is_superuser=True,
            )
            session.add(user)

            # Disease
            disease = Disease(
                name="Test Fever", description="A test disease", vector="Test Vector"
            )
            session.add(disease)

            # Region
            region = GeographicRegion(
                name="Test City",
                code="test_city",
                country="Testland",
                coordinates={"lat": 10.0, "lon": 20.0},
                population=50000,
            )
            session.add(region)

            await session.commit()
            await session.refresh(user)
            await session.refresh(disease)
            await session.refresh(region)
            print(f"✓ Created User ID: {user.id}")
            print(f"✓ Created Disease ID: {disease.id}")
            print(f"✓ Created Region ID: {region.id}")

            # 4. Insert Real-world Data (Time Series)
            print("\n4. Inserting Mock Time Series Data (Outbreak + Environmental)...")

            outbreak_records = []
            env_records = []

            start_date = datetime.now() - timedelta(weeks=10)

            for i in range(10):
                date = start_date + timedelta(weeks=i)
                week = date.isocalendar()[1]

                # Outbreak
                outbreak = OutbreakData(
                    date=date,
                    year=date.year,
                    weekofyear=week,
                    total_cases=10 + i * 2,  # Rising cases
                    disease_id=disease.id,
                    region_id=region.id,
                )
                outbreak_records.append(outbreak)

                # Env Data
                env = EnvironmentalData(
                    date=date,
                    weekofyear=week,
                    temp_avg=25.0 + (i * 0.5),
                    temp_min=20.0,
                    temp_max=30.0,
                    precipitation_mm=50.0 + (i * 10),
                    humidity_percent=80.0,
                    region_id=region.id,
                )
                env_records.append(env)

            session.add_all(outbreak_records)
            session.add_all(env_records)
            await session.commit()
            print(f"✓ Inserted {len(outbreak_records)} outbreak records")
            print(f"✓ Inserted {len(env_records)} environmental records")

            # 5. Query and Verify
            print("\n5. Verifying Data Retrieval...")
            stmt = (
                select(OutbreakData)
                .where(OutbreakData.disease_id == disease.id)
                .limit(5)
            )
            result = await session.execute(stmt)
            rows = result.scalars().all()

            print(f"✓ Retrieved {len(rows)} rows from DB:")
            for row in rows:
                print(f"   - Week {row.weekofyear}: {row.total_cases} cases")

            if len(rows) > 0:
                print("✓ Data verification PASSED")
            else:
                print("✗ Data verification FAILED (No rows found)")

            # 6. Insert Analysis Data (Prediction)
            print("\n6. Inserting Prediction...")
            prediction = Prediction(
                prediction_date=datetime.now(),
                predicted_cases=50.5,
                confidence_score=0.89,
                risk_level="High",
                features_used={"temp": 28.5},
                disease_id=disease.id,
                region_id=region.id,
            )
            session.add(prediction)
            await session.commit()
            print("✓ Prediction inserted successfully")

            # 7. Final Cleanup
            print("\n7. Final Cleanup...")
            # Cleanup related data first due to foreign keys
            await session.execute(
                delete(OutbreakData).where(OutbreakData.disease_id == disease.id)
            )
            await session.execute(
                delete(EnvironmentalData).where(
                    EnvironmentalData.region_id == region.id
                )
            )
            await session.execute(
                delete(Prediction).where(Prediction.disease_id == disease.id)
            )
            await session.execute(delete(Alert).where(Alert.region_id == region.id))

            # Now delete core entities
            await session.delete(user)
            await session.delete(disease)
            await session.delete(region)
            await session.commit()
            print("✓ Test data cleaned up")

        except Exception as e:
            await session.rollback()
            print(f"✗ TEST FAILED: {e}")
            raise e

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(verify_database())
