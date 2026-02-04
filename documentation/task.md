# Epidemiology AI - Master Project Plan

## Mission: To architect, build, and deploy a production-grade, AI-powered early warning system for disease outbreaks, showcasing cutting-edge MLOps, data engineering, and full-stack development practices.

---

### **Phase 0: Foundation & Environment Setup (Weeks 1-2)**

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

### **Phase 1: Core Infrastructure & Database (Weeks 3-5)**

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
- [ ] **Authentication & Authorization Service**
  - [ ] Implement JWT-based authentication: `login`, `register`, and `refresh` endpoints.
  - [ ] Develop a role-based access control (RBAC) dependency for securing admin-only endpoints.

---

### **Phase 2: Data Engineering & ETL Pipeline (Weeks 4-6)**

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

---

### **Phase 3: Machine Learning & MLOps (Weeks 6-10)**

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

### **Phase 4: API & Frontend Integration (Weeks 8-14)**

**Goal:** Build a polished, data-driven frontend and the backing API endpoints.

- [ ] **Backend API Development**
  - [ ] Build out all analytics and dashboard endpoints (`/dashboard/overview`, `/analytics/trends`, `/dashboard/map-data`).
  - [ ] Implement a full CRUD API for `Alerts` management, including acknowledgment and resolution.
- [ ] **Frontend Scaffolding**
  - [ ] Implement routing (`react-router-dom`), state management (`zustand`), and a UI library (e.g., Material-UI).
  - [ ] Create a secure API client with `axios` that handles JWT tokens.
- [ ] **Core UI Implementation**
  - [ ] **Dashboard:** Build summary cards, an interactive map (Leaflet/Mapbox) showing risk zones, and a real-time alerts widget.
  - [ ] **Analytics Views:** Implement dynamic line charts (Recharts) for trend analysis and feature importance.
  - [ ] **Alert Center:** Create a data grid to view, filter, and manage alerts.
- [ ] **Testing & Quality Assurance**
  - [ ] **Unit Testing:** Achieve >80% test coverage for the backend using `pytest`.
  - [ ] **Integration Testing:** Write tests to ensure API endpoints interact correctly with the database.
  - [ ] **Frontend Testing:** Implement component tests for critical UI elements.
  - [ ] **Security:** Integrate `safety` and `npm audit` into the CI pipeline to scan for vulnerable dependencies.

---

### **Phase 5: Deployment & Finalization (Weeks 15-18)**

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
