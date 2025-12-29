# Epidemiology AI - Backend Architecture

## 1. Database Schema Design

### 1.1 Core Tables

#### users
```sql
id: UUID (Primary Key)
email: VARCHAR(255) (Unique, Not Null)
password_hash: VARCHAR(255) (Not Null)
first_name: VARCHAR(100)
last_name: VARCHAR(100)
organization: VARCHAR(255)
role: ENUM('admin', 'health_official', 'analyst', 'researcher')
is_active: BOOLEAN (Default: true)
created_at: TIMESTAMP (Default: now())
updated_at: TIMESTAMP (Default: now())
```

#### diseases
```sql
id: UUID (Primary Key)
name: VARCHAR(100) (Not Null, Unique)
description: TEXT
transmission_type: VARCHAR(100) (e.g., 'vector-borne', 'airborne', 'waterborne')
seasonal_pattern: VARCHAR(255) (e.g., 'monsoon', 'winter', 'year-round')
created_at: TIMESTAMP (Default: now())
updated_at: TIMESTAMP (Default: now())
```

#### geographic_regions
```sql
id: UUID (Primary Key)
name: VARCHAR(255) (Not Null)
region_type: ENUM('country', 'state', 'district', 'city', 'pincode')
latitude: DECIMAL(10, 8)
longitude: DECIMAL(11, 8)
population: INTEGER
area_sqkm: DECIMAL(10, 2)
parent_region_id: UUID (Foreign Key to self)
created_at: TIMESTAMP (Default: now())
updated_at: TIMESTAMP (Default: now())
```

#### outbreak_data
```sql
id: UUID (Primary Key)
disease_id: UUID (Foreign Key to diseases)
region_id: UUID (Foreign Key to geographic_regions)
date: DATE (Not Null)
case_count: INTEGER (Not Null, Default: 0)
hospitalization_count: INTEGER (Default: 0)
death_count: INTEGER (Default: 0)
recovered_count: INTEGER (Default: 0)
data_source: VARCHAR(100) (e.g., 'government', 'hospital', 'survey')
is_preliminary: BOOLEAN (Default: false)
created_at: TIMESTAMP (Default: now())
updated_at: TIMESTAMP (Default: now())

Index: (disease_id, region_id, date) - for time-series queries
Index: (region_id, date) - for geographic time-series
```

#### environmental_data
```sql
id: UUID (Primary Key)
region_id: UUID (Foreign Key to geographic_regions)
date: DATE (Not Null)
temperature_avg: DECIMAL(5, 2) (Celsius)
temperature_min: DECIMAL(5, 2) (Celsius)
temperature_max: DECIMAL(5, 2) (Celsius)
rainfall_mm: DECIMAL(7, 2)
humidity_avg: DECIMAL(5, 2) (Percentage)
wind_speed_avg: DECIMAL(5, 2) (km/h)
vector_index: DECIMAL(5, 2) (e.g., mosquito breeding index)
data_source: VARCHAR(100) (e.g., 'weather_station', 'satellite', 'model')
created_at: TIMESTAMP (Default: now())
updated_at: TIMESTAMP (Default: now())

Index: (region_id, date) - for time-series queries
Index: (date) - for date-based filtering
```

#### digital_signals
```sql
id: UUID (Primary Key)
region_id: UUID (Foreign Key to geographic_regions)
disease_id: UUID (Foreign Key to diseases, optional)
date: DATE (Not Null)
signal_type: ENUM('search_trend', 'social_media', 'pharmacy_sales', 'mobility')
signal_source: VARCHAR(100) (e.g., 'google_trends', 'twitter', 'pharmacy_network')
signal_value: DECIMAL(10, 4) (Normalized score)
signal_volume: INTEGER (Count of mentions/searches)
is_anomaly: BOOLEAN (Computed field)
created_at: TIMESTAMP (Default: now())
updated_at: TIMESTAMP (Default: now())

Index: (region_id, disease_id, date, signal_type) - for multi-dimensional queries
Index: (signal_type, date) - for signal-based analysis
```

#### predictions
```sql
id: UUID (Primary Key)
disease_id: UUID (Foreign Key to diseases)
region_id: UUID (Foreign Key to geographic_regions)
prediction_date: DATE (Not Null, the date being predicted)
actual_date: DATE (When prediction is validated with actual data)
prediction_type: ENUM('risk_score', 'case_count', 'outbreak_probability')
predicted_value: DECIMAL(10, 4)
confidence_interval_lower: DECIMAL(10, 4)
confidence_interval_upper: DECIMAL(10, 4)
model_version: VARCHAR(50)
features_used: JSONB
risk_level: ENUM('low', 'medium', 'high', 'critical')
is_alert_triggered: BOOLEAN (Default: false)
created_at: TIMESTAMP (Default: now())
updated_at: TIMESTAMP (Default: now())

Index: (disease_id, region_id, prediction_date) - for prediction lookup
Index: (prediction_date, risk_level) - for alert filtering
```

#### alerts
```sql
id: UUID (Primary Key)
prediction_id: UUID (Foreign Key to predictions)
user_id: UUID (Foreign Key to users, optional - for assigned alerts)
region_id: UUID (Foreign Key to geographic_regions)
disease_id: UUID (Foreign Key to diseases)
alert_type: ENUM('outbreak_prediction', 'risk_elevation', 'anomaly_detected', 'trend_change')
severity: ENUM('info', 'warning', 'high', 'critical') (Default: 'warning')
title: VARCHAR(500) (Not Null)
description: TEXT
is_acknowledged: BOOLEAN (Default: false)
acknowledged_by: UUID (Foreign Key to users)
acknowledged_at: TIMESTAMP
is_resolved: BOOLEAN (Default: false)
resolved_by: UUID (Foreign Key to users)
resolved_at: TIMESTAMP
created_at: TIMESTAMP (Default: now())
updated_at: TIMESTAMP (Default: now())

Index: (region_id, disease_id, created_at) - for alert history
Index: (severity, is_resolved, created_at) - for alert management
```

#### model_versions
```sql
id: UUID (Primary Key)
model_name: VARCHAR(255) (Not Null)
model_version: VARCHAR(50) (Not Null)
model_type: VARCHAR(100) (e.g., 'xgboost', 'random_forest', 'lstm')
training_date: DATE (Not Null)
training_data_range_start: DATE
training_data_range_end: DATE
model_metrics: JSONB (accuracy, precision, recall, etc.)
model_artifact_path: VARCHAR(500) (Path to stored model)
is_active: BOOLEAN (Default: true)
created_at: TIMESTAMP (Default: now())
updated_at: TIMESTAMP (Default: now())

Index: (model_name, model_version) - for version tracking
Index: (model_name, is_active) - for active model lookup
```

### 1.2 Relationship Tables

#### user_region_access
```sql
id: UUID (Primary Key)
user_id: UUID (Foreign Key to users)
region_id: UUID (Foreign Key to geographic_regions)
access_level: ENUM('read', 'read_write', 'admin')
created_at: TIMESTAMP (Default: now())

Unique: (user_id, region_id) - prevent duplicate access
```

#### disease_symptoms
```sql
id: UUID (Primary Key)
disease_id: UUID (Foreign Key to diseases)
symptom_name: VARCHAR(255) (Not Null)
is_primary: BOOLEAN (Default: false)
created_at: TIMESTAMP (Default: now())

Index: (disease_id) - for symptom lookup by disease
```

## 2. API Endpoint Specifications

### 2.1 Authentication Endpoints

#### POST /api/v1/auth/login
- **Description**: User authentication
- **Request Body**:
  ```json
  {
    "email": "string",
    "password": "string"
  }
  ```
- **Response**:
  ```json
  {
    "access_token": "string",
    "token_type": "string",
    "user": {
      "id": "string",
      "email": "string",
      "role": "string"
    }
  }
  ```

#### POST /api/v1/auth/register
- **Description**: User registration
- **Request Body**:
  ```json
  {
    "email": "string",
    "password": "string",
    "first_name": "string",
    "last_name": "string",
    "organization": "string"
  }
  ```

#### POST /api/v1/auth/refresh
- **Description**: Token refresh
- **Request Body**:
  ```json
  {
    "refresh_token": "string"
  }
  ```

### 2.2 Disease Management Endpoints

#### GET /api/v1/diseases
- **Description**: List all diseases
- **Query Params**:
  - `limit`: number (default: 100)
  - `offset`: number (default: 0)
- **Response**:
  ```json
  {
    "data": [
      {
        "id": "string",
        "name": "string",
        "description": "string",
        "transmission_type": "string",
        "seasonal_pattern": "string"
      }
    ],
    "pagination": {
      "total": 0,
      "limit": 100,
      "offset": 0
    }
  }
  ```

#### GET /api/v1/diseases/{disease_id}
- **Description**: Get specific disease details

#### POST /api/v1/diseases
- **Description**: Create new disease (admin only)
- **Request Body**:
  ```json
  {
    "name": "string",
    "description": "string",
    "transmission_type": "string",
    "seasonal_pattern": "string"
  }
  ```

### 2.3 Data Ingestion Endpoints

#### POST /api/v1/data/outbreaks
- **Description**: Ingest outbreak data
- **Request Body**:
  ```json
  [
    {
      "disease_id": "string",
      "region_id": "string",
      "date": "2023-01-01",
      "case_count": 0,
      "data_source": "string"
    }
  ]
  ```

#### POST /api/v1/data/environmental
- **Description**: Ingest environmental data
- **Request Body**:
  ```json
  [
    {
      "region_id": "string",
      "date": "2023-01-01",
      "temperature_avg": 25.5,
      "rainfall_mm": 10.0
    }
  ]
  ```

#### POST /api/v1/data/digital-signals
- **Description**: Ingest digital surveillance signals
- **Request Body**:
  ```json
  [
    {
      "region_id": "string",
      "disease_id": "string",
      "date": "2023-01-01",
      "signal_type": "search_trend",
      "signal_value": 75.0,
      "signal_source": "google_trends"
    }
  ]
  ```

### 2.4 Prediction & Analytics Endpoints

#### GET /api/v1/predictions
- **Description**: Get predictions with filtering
- **Query Params**:
  - `disease_id`: string
  - `region_id`: string
  - `start_date`: date
  - `end_date`: date
  - `risk_level`: string (low|medium|high|critical)
- **Response**:
  ```json
  {
    "data": [
      {
        "id": "string",
        "disease_id": "string",
        "region_id": "string",
        "prediction_date": "2023-01-01",
        "predicted_value": 15.5,
        "confidence_interval_lower": 10.0,
        "confidence_interval_upper": 20.0,
        "risk_level": "medium"
      }
    ]
  }
  ```

#### POST /api/v1/predictions/generate
- **Description**: Trigger prediction generation
- **Request Body**:
  ```json
  {
    "disease_id": "string",
    "region_id": "string",
    "prediction_horizon_days": 7
  }
  ```

#### GET /api/v1/analytics/trends
- **Description**: Get trend analysis
- **Query Params**:
  - `disease_id`: string (required)
  - `region_id`: string (required)
  - `start_date`: date (required)
  - `end_date`: date (required)
  - `aggregation_period`: string (daily|weekly|monthly)

### 2.5 Dashboard & Visualization Endpoints

#### GET /api/v1/dashboard/overview
- **Description**: Get dashboard overview data
- **Query Params**:
  - `region_id`: string (optional)
- **Response**:
  ```json
  {
    "total_alerts": 0,
    "active_outbreaks": 0,
    "at_risk_regions": 5,
    "prediction_accuracy": 92.5,
    "data_completeness": 85.0
  }
  ```

#### GET /api/v1/dashboard/map-data
- **Description**: Get geospatial data for map visualization
- **Query Params**:
  - `disease_id`: string
  - `date`: date
- **Response**:
  ```json
  {
    "regions": [
      {
        "region_id": "string",
        "region_name": "string",
        "latitude": 12.345,
        "longitude": 67.890,
        "risk_level": "high",
        "case_count": 15,
        "prediction_score": 0.78
      }
    ]
  }
  ```

### 2.6 Alert Management Endpoints

#### GET /api/v1/alerts
- **Description**: Get alerts with filtering
- **Query Params**:
  - `region_id`: string
  - `disease_id`: string
  - `severity`: string (info|warning|high|critical)
  - `status`: string (active|acknowledged|resolved)
  - `assigned_to`: string (user_id)

#### POST /api/v1/alerts/{alert_id}/acknowledge
- **Description**: Acknowledge an alert
- **Request Body**:
  ```json
  {
    "notes": "string"
  }
  ```

#### POST /api/v1/alerts/{alert_id}/resolve
- **Description**: Mark an alert as resolved
- **Request Body**:
  ```json
  {
    "resolution_notes": "string",
    "action_taken": "string"
  }
  ```

### 2.7 Administrative Endpoints

#### GET /api/v1/admin/system-status
- **Description**: Get system health status
- **Response**:
  ```json
  {
    "status": "healthy",
    "services": {
      "api": "running",
      "ml_service": "running",
      "database": "connected",
      "cache": "connected"
    },
    "data_latency": "5 minutes",
    "prediction_queue_size": 0
  }
  ```

#### GET /api/v1/admin/model-performance
- **Description**: Get model performance metrics
- **Query Params**:
  - `model_name`: string
  - `start_date`: date
  - `end_date`: date

## 3. API Design Principles

### 3.1 Security
- All endpoints require authentication except health checks
- Role-based access control (RBAC) for sensitive operations
- Input validation and sanitization
- Rate limiting to prevent abuse
- HTTPS enforcement

### 3.2 Performance
- Pagination for all list endpoints
- Caching for frequently accessed data
- Asynchronous processing for heavy operations
- Query optimization with proper indexing

### 3.3 Error Handling
- Consistent error response format:
  ```json
  {
    "error": {
      "code": "string",
      "message": "string",
      "details": "object"
    }
  }
  ```

### 3.4 Versioning
- API versioning in URL path (e.g., /api/v1/)
- Backward compatibility maintained when possible
- Deprecation notices for deprecated endpoints

## 4. Data Flow Architecture

### 4.1 Ingestion Flow
1. External data sources push to ingestion endpoints
2. Data validation and cleaning in real-time
3. Storage in appropriate tables
4. Trigger analytics and prediction jobs

### 4.2 Prediction Flow
1. Scheduled or triggered prediction jobs
2. Feature extraction from historical data
3. Model inference using active models
4. Prediction storage and alert generation
5. Dashboard update with new predictions

### 4.3 Alerting Flow
1. Prediction models identify high-risk scenarios
2. Automatic alert generation based on thresholds
3. Notification to relevant users
4. Dashboard highlighting of alerts
5. User acknowledgment and resolution tracking