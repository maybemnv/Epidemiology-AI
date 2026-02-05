# Epidemiology AI - Master Project Plan

## This document outlines the actionable tasks required to fully operationalize the Epidemiology AI project. It is based on the comprehensive documentation provided and structured to guide development from setup to production deployment.

### Phase 0: Foundation & Environment Setup

**Goal:** Establish a rock-solid, professional-grade development environment.

- [x] **System & Tooling Verification**
  - [x] Install Python 3.11+, Node.js v18+, Docker, PostgreSQL 14+, and Git.
- [x] **Repository & CI/CD Setup**
  - [x] Initialize Git repository with a professional README.
  - [x] Configure `.gitignore` and `.dockerignore` for Python, Node, and IDE artifacts.
  - [x] **Implement Pre-commit Hooks:** Enforce code quality automatically using `black`, `flake8`, `isort`.
- [x] **Backend Environment (Python)**
  - [x] Create and activate a virtual environment (`.venv`).
  - [x] Lock dependencies using `pip freeze > requirements.txt`.
  - [x] Configure `pyproject.toml` to manage formatter and linter settings.
- [x] **Frontend Environment (React)**
  - [x] Initialize a Vite-based React + TypeScript project in `/frontend`.
  - [x] Install and configure ESLint and Prettier for consistent code style.
- [x] **Configuration & Secrets Management**
  - [x] Create a `.env.example` file for environment variable schema.
  - [x] Load secrets securely using `python-dotenv`; never commit the `.env` file.

---

### Phase 1: Core Infrastructure & Database

**Goal:** Build the skeletal structure of the backend, including the database and core API services.

- [x] **Database Architecture & Implementation**
  - [x] Design a normalized schema (Ref: `backend_architecture.md`).
  - [x] **Setup Alembic Migrations:** Manage all future schema changes programmatically.
  - [x] Create initial migrations for all core, data, and analysis tables (`users`, `outbreak_data`, etc.).
  - [x] **Enable TimescaleDB:** Convert `outbreak_data` and `environmental_data` to hypertables for time-series performance.
- [x] **API Framework Initialization**
  - [x] Setup a modular FastAPI application structure (`/src/api`, `/src/core`, `/src/models`).
  - [x] Implement robust SQLAlchemy `database.py` with an async connection engine.
  - [x] Configure CORS middleware and global exception handlers for clean error responses.
- [x] **Authentication & Authorization Service**
  - [x] Implement JWT-based authentication: `login`, `register`, and `refresh` endpoints.
  - [x] Develop a role-based access control (RBAC) dependency for securing admin-only endpoints.

---

### \*\*Phase 2: Data Engineering & ETL Pipeline

**Goal:** Build an automated and reliable data pipeline.

- [ ] **Automated Data Ingestion Service**
  - [ ] Develop a modular service in `/src/services/ingestion/`.
  - [ ] **Weather Module**: Create a client for the NOAA API to fetch data for configured regions.
  - [ ] **Disease Data Module**: Implement a robust importer for the DrivenData CSVs.
  - [ ] **Digital Signals Module**: Integrate the `pytrends` library to fetch Google Trends data.
- [ ] **ETL Workflow & Scheduling**
  - [ ] **Implement Celery:** Use Celery with Redis for scheduling and running asynchronous data ingestion tasks.
  - [ ] Create a nightly task to fetch the latest data from all Tier 2 sources.
  - [ ] Develop a robust ETL pipeline that cleans, validates (with Pydantic), and normalizes all incoming data before loading it into the database.
  - [ ] **Cleaning**: Handle missing values (forward/backward fill), detect outliers.
  - [ ] **Normalization**: Standardize units (Kelvin to Celsius, dates to ISO8601).
  - [ ] **Validation**: Pydantic models to validate incoming data schema.
  - [ ] **Loading**: Bulk insert functions for high-volume data.

---

### Phase 3: Machine Learning & MLOps

**Goal:** Develop, train, and serve a highly accurate predictive model with a clear path for operationalization.

- [x] **Advanced Feature Engineering**
  - [x] Create a reproducible feature engineering pipeline: Temporal features, lag features, rolling statistics, and vegetation indices.
- [x] **Model Development & Training**
  - [x] **Location-Specific Models**: Refactor the training pipeline to produce separate, optimized models for San Juan ('sj') and Iquitos ('iq').
  - [x] Train baseline (Random Forest) and advanced (XGBoost) models for each location.
  - [x] **Implement Hyperparameter Tuning:** Use Grid Search or Optuna to find the optimal parameters.
  - [x] Serialize final model artifacts using `joblib`.
- [ ] **Model Serving & API**
  - [x] Implement `Predictor` service that dynamically loads the correct model based on the request's region.
  - [x] `POST /api/predict`: Live prediction endpoint.
  - [x] `GET /api/model/stats`: Endpoint to return key metrics for the currently loaded model.
- [ ] **MLOps - The Professional Edge**
  - [ ] **Integrate MLflow:**
    - [ ] Track all training runs, parameters, and metrics automatically.
    - [ ] Log model artifacts and feature importance plots.
    - [ ] Create a "champion/challenger" workflow for promoting models.
  - [ ] **Automate Retraining:** Create a scheduled Celery task to retrain models weekly/monthly on new data and log results to MLflow.
  - [ ] **Implement Model Monitoring:**
    - [ ] Persist all predictions and inputs to the `predictions` table.
    - [ ] Create a service to monitor for **prediction drift** (accuracy degradation over time) and **data drift** (changes in input feature distribution).
    - [ ] Set up alerts if model performance drops below a predefined threshold.

---

### Phase 4: API & Frontend Integration

**Goal:** Build a polished, data-driven frontend and the backing API endpoints.

- [ ] **Backend API Development**
  - [ ] **Disease Management**
  - [ ] `GET /api/v1/diseases`: List supported diseases.
  - [ ] `POST /api/v1/diseases`: Add new disease config (Admin).
- [ ] **Region Management**
  - [ ] `GET /api/v1/regions`: GeoJSON/List of monitored areas.
  - [ ] `GET /api/v1/regions/{id}/stats`: Aggregate stats for a region.
- [ ] **Analytics & Dashboard Endpoints**
  - [ ] `GET /api/v1/dashboard/overview`: High-level metrics (Active Alerts, Risk Count).
  - [ ] `GET /api/v1/analytics/trends`: Time-series data for charting (cases vs. prediction).
  - [ ] `GET /api/v1/dashboard/map-data`: Geospatial risk heatmap data.
  - [ ] Implement a full CRUD API for `Alerts` management, including acknowledgment and resolution.
- [ ] **Frontend Scaffolding**
  - [ ] Implement routing (`react-router-dom`), state management (`zustand`), and a UI library (e.g., Material-UI).
  - [ ] Create a secure API client with `axios` that handles JWT tokens.

  ## Phase 6: Advanced Features & Integration

**Goal:** Add polish and production-ready capabilities.

- [ ] **Alert Engine** (Backend)
  - [ ] Scheduled task (Celery/Cron) to run predictions daily.
  - [ ] Logic to trigger alerts if `predicted_cases > threshold`.
  - [ ] Email/SMS notification integration (SMTP/Twilio).
- [ ] **Multi-Disease Support**
  - [ ] Refactor Predictor to select model based on `disease_id`.
  - [ ] Train separate models for Dengue, Malaria, etc.
- [ ] **Reporting**
  - [ ] PDF Generation endpoint: Automated weekly report.
  - [ ] CSV Export for raw data.

## Phase 5: Frontend Development

**Goal:** Create an intuitive UI for public health officials. (Ref: `frontend_ux_design.md`)

- [ ] **Project scaffolding**
  - [ ] Setup Routing (`react-router-dom`).
  - [ ] Setup State Management (`zustand` or `redux-toolkit`).
  - [ ] Setup UI Library (MUI/AntD) and Tailwind CSS.
- [ ] **Authentication UI**
  - [ ] Login Page.
  - [ ] Registration Page.
  - [ ] Protected Route wrapper.
- [ ] **Dashboard Implementation**
  - [ ] **Summary Cards**: Active alerts, Prediction accuracy, At-risk regions.
  - [ ] **Interactive Map**: Leaflet/Mapbox integration showing risk zones.
  - [ ] **Recent Alerts Widget**: List of high-priority notifications.
- [ ] **Analytics Views**
  - [ ] **Trend Analysis**: Line charts (Recharts/Chart.js) comparing Actual vs. Predicted cases.
  - [ ] **Factor Analysis**: Bar charts showing feature importance (Rainfall vs. Cases).
- [ ] **Alert Center**
  - [ ] Data Grid view of all alerts.
  - [ ] Filtering (Severity, Region, Date).
  - [ ] Detail view with action buttons (Acknowledge/Resolve).
- [ ] **Model Performance View**
  - [ ] Visualization of R²/RMSE over time.
  - [ ] Confusion matrix for outbreak classification.

---

### Phase 5: Deployment & Finalization

**Goal:** Deploy the application to production and finalize all documentation.

- [ ] **Containerization & Deployment**
  - [ ] Write optimized, multi-stage `Dockerfile` for both the backend and frontend.
  - [ ] Create a production-ready `docker-compose.yml` defining all services (API, frontend, DB, Redis, Celery).
- [ ] **CI/CD Pipeline (GitHub Actions)**
  - [ ] Create a workflow that automatically runs tests and linters on every pull request.
  - [ ] On merge to `main`, the workflow should build and push Docker images to a registry (e.g., Docker Hub, GHCR).
- [ ] **Production Monitoring**
  - [ ] Integrate Prometheus for scraping application metrics.
  - [ ] Set up a Grafana dashboard to visualize system health, API latency, and key model performance metrics.
- [ ] **Final Documentation**
  - [ ] Ensure the auto-generated FastAPI docs (`/docs`) are clean and comprehensive.
  - [ ] Write a high-level `README.md` that links to the `DATA_STRATEGY.md` and this `task.md` file.
  - [ ] Create a `DEPLOYMENT.md` guide explaining how to launch the entire system with Docker Compose.
- [ ] **Unit Testing**: Backend (`pytest`) coverage > 80%.
- [ ] **Integration Testing**: API endpoints functional with DB.
- [ ] **Frontend Testing**: Critical user flows (Login -> Dashboard -> Alert).
- [ ] **Security Scan**: Check dependencies for vulnerabilities (`safety`, `npm audit`).
- [ ] **Performance**: Ensure API response time < 200ms for dashboard data.
