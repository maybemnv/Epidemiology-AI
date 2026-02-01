# Epidemiology AI: Disease Outbreak Early Warning System

> **Quick Start**: Run `python main.py` for instructions, or jump straight to [QUICKSTART.md](QUICKSTART.md) for a 5-minute demo!

## Overview

Epidemiology AI is an AI-powered system that analyzes real-time data from multiple sources to predict potential disease outbreaks earlier than traditional surveillance methods. Our solution combines epidemiological data, climate data, social indicators, and environmental factors to provide early warning alerts to public health officials.

## Problem Statement

Public health officials need to detect outbreaks of diseases (like dengue, COVID-19, or diarrheal diseases) as early as possible to contain them. Traditional surveillance can be slow – by the time many cases are confirmed, the disease may have spread. Especially in India's dense populations, a delayed response can lead to large-scale outbreaks. We need smarter systems that analyze various signals to predict or detect outbreaks sooner.

## Solution Approach

Our system creates an AI system that analyzes real-time data and raises alerts for potential disease outbreaks. This involves a combination of data sources:

- Health clinic reports
- Pharmacy sales (e.g., spike in certain medication sales)
- Social media or Google search trends
- Weather conditions (since climate affects diseases)

A machine learning model learns the normal pattern and detects anomalies indicating an outbreak, using time-series analysis to predict outbreak probability.

## Key Features

- **Multi-source Data Integration**: Aggregates data from health surveillance systems, weather services, social media, and search trends
- **Real-time Prediction Engine**: Uses advanced ML models to predict outbreaks 2-4 weeks earlier than traditional methods
- **Interactive Dashboard**: Provides geospatial visualization and trend analysis
- **Automated Alert System**: Generates risk-based alerts for public health officials
- **Multi-disease Support**: Initially focused on dengue, with capability to expand to other diseases

## Technology Stack

- **Backend**: Python, FastAPI, scikit-learn, XGBoost
- **Frontend**: React/TypeScript with D3.js for visualization
- **Database**: PostgreSQL with TimescaleDB for time-series data
- **ML Models**: Time-series forecasting, anomaly detection, ensemble methods
- **Deployment**: Docker, Kubernetes

## Repository Structure

```
D:\Projects\Epidemiology AI\
├── data/              # Data files and datasets
├── documentation/     # Project documentation and design specs
├── frontend/          # React/TypeScript frontend application
├── migrations/        # Database migrations (Alembic)
├── models/            # Trained ML models
├── notebooks/         # Jupyter notebooks for data analysis
├── src/               # Backend source code
│   ├── api/           # API Endpoints (FastAPI)
│   ├── database/      # Database models and core logic
│   └── models/        # ML prediction logic
├── tests/             # Test files
├── main.py            # Entry point for the application
├── pyproject.toml     # Project dependencies and config
├── alembic.ini        # Migration configuration
└── requirements.txt   # Python dependencies
```

## How to Run the Prototype

1. **Install Dependencies**:
   We recommended using `uv` for fast dependency management, but `pip` works too.

   ```bash
   pip install -r requirements.txt
   # OR
   uv sync
   ```

2. **Setup Database**:
   Ensure PostgreSQL is running, then apply migrations:

   ```bash
   # Make sure .env has correct DATABASE_URL
   alembic upgrade head
   ```

3. **Run the Application**:

   ```bash
   uv run main.py
   ```

This will run the prototype that demonstrates the core concept of using multiple data sources and machine learning to predict disease outbreaks.

## Documentation

The `documentation/` folder contains comprehensive documentation for the project:

### Getting Started

- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute demo guide
- **[data-guide.md](documentation/data-guide.md)** - How to acquire datasets
- **[setup-guide.md](documentation/setup-guide.md)** - Installation & troubleshooting

### Design Documents

- `PRD.md` - Product Requirements Document
- `system_architecture.md` - System architecture design
- `backend_architecture.md` - Backend API schemas and database design
- `frontend_ux_design.md` - Frontend UI/UX design specifications
- `tech_stack.md` - Technology stack and concepts
- `data_sources.md` - Data sources and API research
- `timeline_milestones.md` - Project timeline and milestones
- `goals.md` - Project goals and success metrics
- `Problem statement.md` - Original problem description

## Innovation & Impact

Our system addresses the critical need for early disease outbreak detection by combining multiple data streams with advanced ML techniques. This approach can significantly reduce response time, prevent large-scale outbreaks, and save lives, particularly in densely populated regions.

## Expected Outcomes

- 50-70% improvement in early outbreak detection
- 90% accuracy in outbreak predictions
- Reduction in false positive alerts to less than 10%
- Scalable solution applicable to multiple diseases and regions

## Current Status

- Complete system architecture and technical specifications
- Data source research and API integration planning
- Frontend and backend design specifications
- ML model development framework
- Ready for implementation phase
