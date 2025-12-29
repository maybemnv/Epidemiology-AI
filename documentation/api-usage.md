# API Usage Guide

## Quick Start

### 1. Train the Model

First, run the Jupyter notebook to train and save the model:

```bash
jupyter notebook
# Open: notebooks/dengue_outbreak_prediction.ipynb
# Run all cells - model will be saved to models/dengue_outbreak_predictor.pkl
```

### 2. Start the API Server

```bash
cd src
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`

### 3. Access Documentation

Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI)

---

## API Endpoints

### Health Check

**GET** `/health`

Check if API and model are running correctly.

```bash
curl http://localhost:8000/health
```

Response:

```json
{
  "status": "healthy",
  "timestamp": "2025-12-29T18:00:00",
  "model_status": "loaded"
}
```

---

### Make Prediction

**POST** `/api/predict`

Predict dengue outbreak risk.

**Request Body:**

```json
{
  "temp_avg": 27.5,
  "temp_min": 22.0,
  "temp_max": 33.0,
  "precipitation_mm": 45.2,
  "humidity_percent": 78.5,
  "weekofyear": 24,
  "previous_cases": [12, 15, 18, 22]
}
```

**Response:**

```json
{
  "predicted_cases": 25.3,
  "risk_level": "Medium",
  "confidence": 0.82,
  "outbreak_threshold": 30.5,
  "features_used": 18,
  "timestamp": "2025-12-29T18:00:00"
}
```

**Python Example:**

```python
import requests

url = "http://localhost:8000/api/predict"
data = {
    "temp_avg": 27.5,
    "temp_min": 22.0,
    "temp_max": 33.0,
    "precipitation_mm": 45.2,
    "humidity_percent": 78.5,
    "weekofyear": 24,
    "previous_cases": [12, 15, 18, 22]
}

response = requests.post(url, json=data)
print(response.json())
```

**cURL Example:**

```bash
curl -X POST "http://localhost:8000/api/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "temp_avg": 27.5,
    "temp_min": 22.0,
    "temp_max": 33.0,
    "precipitation_mm": 45.2,
    "humidity_percent": 78.5,
    "weekofyear": 24,
    "previous_cases": [12, 15, 18, 22]
  }'
```

---

### Get Model Statistics

**GET** `/api/model/stats`

Get model performance metrics and metadata.

```bash
curl http://localhost:8000/api/model/stats
```

Response:

```json
{
  "status": "loaded",
  "model_type": "XGBoost",
  "features_count": 18,
  "outbreak_threshold": 30.5,
  "performance_metrics": {
    "MAE": 5.23,
    "RMSE": 7.18,
    "R2": 0.82
  }
}
```

---

### Reload Model

**POST** `/api/model/reload`

Reload the model from disk (useful after retraining).

```bash
curl -X POST http://localhost:8000/api/model/reload
```

---

## Request Parameters

### Weather Data

| Parameter          | Type  | Range     | Description                  |
| ------------------ | ----- | --------- | ---------------------------- |
| `temp_avg`         | float | -50 to 60 | Average temperature in °C    |
| `temp_min`         | float | -50 to 60 | Minimum temperature in °C    |
| `temp_max`         | float | -50 to 60 | Maximum temperature in °C    |
| `precipitation_mm` | float | 0+        | Precipitation in millimeters |
| `humidity_percent` | float | 0-100     | Relative humidity percentage |
| `weekofyear`       | int   | 1-53      | ISO week number              |

### Historical Cases

| Parameter        | Type      | Description                           |
| ---------------- | --------- | ------------------------------------- |
| `previous_cases` | List[int] | 1-4 most recent weeks of dengue cases |

**Important:** Provide at least 1 week, up to 4 weeks of historical data for best predictions.

---

## Response Fields

| Field                | Type     | Description                      |
| -------------------- | -------- | -------------------------------- |
| `predicted_cases`    | float    | Predicted number of dengue cases |
| `risk_level`         | string   | "Low", "Medium", or "High"       |
| `confidence`         | float    | Prediction confidence (0-1)      |
| `outbreak_threshold` | float    | Cases threshold for outbreak     |
| `features_used`      | int      | Number of features in model      |
| `timestamp`          | datetime | Prediction timestamp             |

---

## Risk Levels

- **Low**: Predicted cases < 50% of outbreak threshold
- **Medium**: Predicted cases between 50-100% of threshold
- **High**: Predicted cases > outbreak threshold

---

## Error Handling

### Model Not Loaded (503)

```json
{
  "detail": "Model not loaded. Please train and save a model first."
}
```

**Solution:** Run the Jupyter notebook to train the model.

### Invalid Input (422)

```json
{
  "detail": [
    {
      "loc": ["body", "weekofyear"],
      "msg": "ensure this value is greater than or equal to 1",
      "type": "value_error"
    }
  ]
}
```

**Solution:** Check input parameter ranges and types.

---

## Testing the API

### Using Swagger UI

1. Go to `http://localhost:8000/docs`
2. Click on an endpoint
3. Click "Try it out"
4. Fill in the request body
5. Click "Execute"

### Using Postman

1. Import the collection: `File > Import > Link`
2. Enter: `http://localhost:8000/openapi.json`
3. Select imported collection
4. Edit request body and send

### Automated Testing

```bash
# Run tests (if implemented)
pytest tests/test_api.py
```

---

## Architecture

```
src/
├── main.py              # FastAPI app & startup
├── api/
│   └── routes.py        # API endpoints
└── models/
    ├── service.py       # Business logic
    └── predictor.py     # ML model wrapper
```

### Request Flow

1. **Client** → HTTP Request → **FastAPI** (`main.py`)
2. **FastAPI** → Route → **API Routes** (`routes.py`)
3. **Routes** → Service Call → **Model Service** (`service.py`)
4. **Service** → Prediction → **Predictor** (`predictor.py`)
5. **Predictor** → XGBoost Model → **Prediction**
6. **Response** ← Chain back to client

---

## Production Considerations

### Security

- Add API key authentication
- Implement rate limiting
- Use HTTPS only
- Validate and sanitize inputs

### Scalability

- Use async database connections
- Implement caching for model predictions
- Deploy multiple instances with load balancer
- Use model versioning

### Monitoring

- Add logging (structured JSON logs)
- Track prediction latency
- Monitor model drift
- Set up error alerting

---

## Troubleshooting

### Server won't start

- Check if port 8000 is free: `netstat -an | findstr 8000`
- Try different port: `uvicorn main:app --port 8001`

### Model not loading

- Check model file exists: `models/dengue_outbreak_predictor.pkl`
- Verify path in `src/main.py`
- Run notebook to create model

### Predictions seem off

- Check input data ranges
- Verify `previous_cases` array length
- Compare with notebook predictions
- Check model metrics

---

## Next Steps

1. **Frontend Integration**: Connect React dashboard to these endpoints
2. **Database**: Store predictions for tracking
3. **Alerts**: Implement notification system
4. **Multi-region**: Support predictions for multiple locations
5. **Real-time Data**: Integrate weather and case data APIs
