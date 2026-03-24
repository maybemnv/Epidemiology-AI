"""
Celery Tasks

Background tasks for ETL, predictions, and alerts.
"""

from celery import Task
from datetime import datetime, timedelta
import logging
from typing import List

from src.core.celery_app import celery_app
from src.database.core import AsyncSessionLocal
from src.database.models import Disease, GeographicRegion, OutbreakData, Prediction
from src.services.etl import ETLService
from src.services.ingestion.weather import WeatherDataClient
from src.services.ingestion.digital_signals import DigitalSignalsClient
from sqlalchemy import select

logger = logging.getLogger(__name__)


class DBTask(Task):
    """Base task with DB session management"""

    _db = None

    @property
    def db(self):
        if self._db is None:
            self._db = AsyncSessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()


@celery_app.task(base=DBTask, bind=True)
def ingest_weather_data(self, region_ids: List[int] = None):
    """Ingest weather data from NOAA API"""
    logger.info("Starting weather data ingestion task")

    try:
        client = WeatherDataClient()
        db = self.db

        if not region_ids:
            result = db.execute(select(GeographicRegion))
            regions = result.scalars().all()
            region_ids = [r.id for r in regions]

        success_count = 0
        error_count = 0

        for region_id in region_ids:
            try:
                region = db.get(GeographicRegion, region_id)
                if not region or not region.latitude or not region.longitude:
                    logger.warning(f"Region {region_id} has no coordinates")
                    continue

                data = client.fetch_data(
                    lat=float(region.latitude),
                    lon=float(region.longitude),
                    start_date=datetime.now() - timedelta(days=7),
                    end_date=datetime.now(),
                )

                if data:
                    import asyncio

                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    etl = ETLService(db)
                    loop.run_until_complete(etl.ingest_environmental_data(data))
                    loop.close()
                    success_count += 1
                else:
                    error_count += 1

            except Exception as e:
                logger.error(f"Error ingesting weather for region {region_id}: {e}")
                error_count += 1

        logger.info(
            f"Weather ingestion complete: {success_count} success, {error_count} errors"
        )
        return {"success": success_count, "errors": error_count}

    except Exception as e:
        logger.error(f"Weather ingestion task failed: {e}")
        raise


@celery_app.task(base=DBTask, bind=True)
def ingest_digital_signals(self, region_ids: List[int] = None):
    """Ingest digital signals from Google Trends"""
    logger.info("Starting digital signals ingestion task")

    try:
        client = DigitalSignalsClient()
        db = self.db

        if not region_ids:
            result = db.execute(select(GeographicRegion))
            regions = result.scalars().all()
            region_ids = [r.id for r in regions]

        success_count = 0
        error_count = 0

        for region_id in region_ids:
            try:
                region = db.get(GeographicRegion, region_id)
                if not region:
                    continue

                data = client.fetch_data(region_id=region_id, days=7)

                if data:
                    import asyncio

                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    etl = ETLService(db)
                    loop.run_until_complete(etl.ingest_digital_signals(data))
                    loop.close()
                    success_count += 1
                else:
                    error_count += 1

            except Exception as e:
                logger.error(f"Error ingesting signals for region {region_id}: {e}")
                error_count += 1

        logger.info(
            f"Digital signals ingestion complete: {success_count} success, {error_count} errors"
        )
        return {"success": success_count, "errors": error_count}

    except Exception as e:
        logger.error(f"Digital signals task failed: {e}")
        raise


@celery_app.task(base=DBTask, bind=True)
def generate_predictions(self, disease_id: int = None, region_id: int = None):
    """Generate predictions for all disease-region pairs"""
    logger.info("Starting prediction generation task")

    try:
        db = self.db

        query = select(Disease, GeographicRegion)
        if disease_id:
            query = query.where(Disease.id == disease_id)
        if region_id:
            query = query.where(GeographicRegion.id == region_id)

        result = db.execute(query)
        pairs = result.all()

        predictions_generated = 0

        for disease, region in pairs:
            try:
                outbreak_result = db.execute(
                    select(OutbreakData)
                    .where(
                        OutbreakData.disease_id == disease.id,
                        OutbreakData.region_id == region.id,
                    )
                    .order_by(OutbreakData.date.desc())
                    .limit(4)
                )
                recent_outbreaks = outbreak_result.scalars().all()

                if len(recent_outbreaks) < 4:
                    logger.warning(
                        f"Insufficient data for {disease.name} in {region.name}"
                    )
                    continue

                from src.models.service import ModelService

                model_service = ModelService()
                if not model_service.is_model_loaded():
                    logger.warning("Model not loaded, skipping prediction")
                    continue

                latest = recent_outbreaks[0]
                prediction = model_service.predict_outbreak(
                    temp_avg=getattr(latest, "temperature_avg", 25.0),
                    temp_min=getattr(latest, "temperature_min", 20.0),
                    temp_max=getattr(latest, "temperature_max", 30.0),
                    precipitation_mm=getattr(latest, "precipitation_mm", 10.0),
                    humidity_percent=getattr(latest, "humidity_avg", 70.0),
                    weekofyear=latest.date.isocalendar().week,
                    previous_cases=[o.case_count for o in reversed(recent_outbreaks)],
                )

                new_prediction = Prediction(
                    disease_id=disease.id,
                    region_id=region.id,
                    prediction_date=datetime.now() + timedelta(days=7),
                    predicted_value=prediction["predicted_cases"],
                    risk_level=prediction["risk_level"].lower(),
                    model_version="v1.0",
                    features_used=prediction["features_used"],
                    is_alert_triggered=prediction["risk_level"] in ["High", "Critical"],
                )

                db.add(new_prediction)
                predictions_generated += 1

            except Exception as e:
                logger.error(
                    f"Error generating prediction for {disease.name} in {region.name}: {e}"
                )
                continue

        db.commit()
        logger.info(f"Generated {predictions_generated} predictions")
        return {"predictions_generated": predictions_generated}

    except Exception as e:
        logger.error(f"Prediction generation task failed: {e}")
        raise


@celery_app.task(base=DBTask, bind=True)
def check_and_trigger_alerts(self):
    """Check predictions and trigger alerts if thresholds exceeded"""
    logger.info("Starting alert check task")

    try:
        db = self.db

        high_risk_predictions = db.execute(
            select(Prediction).where(
                Prediction.risk_level.in_(["high", "critical"]),
                Prediction.is_alert_triggered.is_(False),
            )
        )
        predictions = high_risk_predictions.scalars().all()

        alerts_created = 0

        for pred in predictions:
            try:
                from src.database.models import Alert, AlertSeverity, AlertType

                alert = Alert(
                    prediction_id=pred.id,
                    region_id=pred.region_id,
                    disease_id=pred.disease_id,
                    alert_type=AlertType.OUTBREAK_PREDICTION,
                    severity=(
                        AlertSeverity.CRITICAL
                        if pred.risk_level == "critical"
                        else AlertSeverity.HIGH
                    ),
                    title=f"Outbreak Alert: {pred.risk_level.capitalize()} Risk",
                    description=f"Predicted {pred.predicted_value} cases for {pred.prediction_date}",
                    is_alert_triggered=True,
                )

                db.add(alert)
                pred.is_alert_triggered = True
                alerts_created += 1

            except Exception as e:
                logger.error(f"Error creating alert for prediction {pred.id}: {e}")
                continue

        db.commit()
        logger.info(f"Created {alerts_created} alerts")
        return {"alerts_created": alerts_created}

    except Exception as e:
        logger.error(f"Alert check task failed: {e}")
        raise
