import asyncio
import sys
import os
from sqlalchemy import select
from datetime import datetime
from src.database.core import AsyncSessionLocal
from src.database.models import Prediction, Alert

sys.path.append(os.getcwd())

THRESHOLD_CASES = 50.0  # Alert threshold


async def check_alerts():
    async with AsyncSessionLocal() as session:
        print(
            f"[{datetime.now()}] Checking for outbreaks "
            f"exceeding {THRESHOLD_CASES} cases..."
        )

        # Find high risk predictions
        stmt = select(Prediction).where(Prediction.predicted_cases > THRESHOLD_CASES)
        result = await session.execute(stmt)
        predictions = result.scalars().all()

        new_alerts = 0

        for pred in predictions:
            # Check if active alert exists for this
            # region/date/prediction

            stmt_alert = select(Alert).where(
                Alert.region_id == pred.region_id,
                Alert.message.contains(f"Predicted {pred.predicted_cases:.1f}"),
            )
            res_alert = await session.execute(stmt_alert)
            if res_alert.scalars().first():
                continue

            # Create Alert
            severity = "Critical" if pred.predicted_cases > 200 else "Warning"
            alert = Alert(
                severity=severity,
                message=(
                    f"High risk detected: Predicted "
                    f"{pred.predicted_cases:.1f} cases for date "
                    f"{pred.prediction_date}"
                ),
                status="New",
                region_id=pred.region_id,
            )
            session.add(alert)
            new_alerts += 1
            print(
                f" -> Alert generated for Region {pred.region_id}: "
                f"{pred.predicted_cases} cases"
            )

        if new_alerts > 0:
            await session.commit()
            print(f"Committed {new_alerts} new alerts.")
        else:
            print("No new alerts needed.")


async def main():
    while True:
        try:
            await check_alerts()
        except Exception as e:
            print(f"Error in alert scheduler: {e}")

        # Sleep for 60 seconds
        print("Sleeping for 60 seconds...")
        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())
