# Epidemiology AI Project Context

## Project Overview

The Epidemiology AI project is a machine learning application focused on early disease outbreak detection and prediction. The system aims to analyze real-time data from multiple sources to identify potential disease outbreaks (such as dengue, COVID-19, or diarrheal diseases) earlier than traditional surveillance methods.

The project implements an AI system that combines various data sources including:

- Epidemiological data (case reports, disease surveillance)
- Climate data (temperature, rainfall, humidity)
- Proxy data (pharmacy sales, social media trends, search patterns)
- Environmental factors (vector breeding conditions)

## Architecture & Technology Stack

- **Backend**: Python-based API using FastAPI
- **Frontend**: React/TypeScript application built with Vite
- **ML Libraries**: scikit-learn, XGBoost, pandas, numpy, matplotlib, seaborn
- **AI/ML Tools**: Google Gen AI, LangChain
- **Visualization**: Matplotlib, Seaborn
- **Containerization**: Docker and Docker Compose
- **Development**: Jupyter notebooks for experimentation

## Project Structure

```
D:\Projects\Epidemiology AI\
├── data/           # Data files and datasets
├── documentation/  # Project documentation and problem statement
├── frontend/       # React/TypeScript frontend application
├── models/         # Trained ML models
├── notebooks/      # Jupyter notebooks for data analysis and experimentation
├── src/            # Backend source code
├── tests/          # Test files
├── main.py         # Entry point for the application
├── pyproject.toml  # Python project configuration
├── Dockerfile      # Containerization instructions
├── compose.yaml    # Docker Compose configuration
└── requirements.txt # Python dependencies
```

## Problem Statement

The project addresses the critical need for early disease outbreak detection. Traditional surveillance methods often result in delayed responses that can lead to large-scale outbreaks, particularly in densely populated areas. This AI system aims to provide early warning capabilities by analyzing multiple data streams to detect anomalies that may indicate an emerging outbreak.

The target use case includes diseases like dengue, COVID-19, and other seasonal diseases with environmental correlations. The system would use time-series analysis and machine learning models to predict outbreak probabilities based on historical patterns combined with real-time data inputs.

## Building and Running

### Backend

1. Install dependencies: `pip install -r requirements.txt`
2. Run with: `python main.py` (default implementation prints "Hello from epidemiology-ai!")
3. To run with FastAPI: `uvicorn main:app --reload` (after implementing FastAPI structure)

### Frontend

1. Navigate to `/frontend`
2. Install dependencies: `npm install`
3. Run development server: `npm run dev`
4. Build for production: `npm run build`

### Docker

1. Build and run with Docker Compose:
   ```
   docker-compose up --build
   ```
2. The application will be available at http://localhost:8000

### Development Commands

- Run tests: `pytest` (using pytest dependency)
- Run Jupyter notebooks: `jupyter notebook` (for analysis and experimentation)

## Current State

The project is in early development with the following characteristics:

- Backend structure defined in `main.py` but with minimal implementation
- Frontend is a React/TypeScript template created with Vite
- Dependencies specified in `pyproject.toml` and `requirements.txt`
- Documentation includes a detailed problem statement
- All major directories exist but are currently empty

## Key Dependencies

- FastAPI: Web framework for backend API
- Pydantic: Data validation
- Pandas/Numpy: Data manipulation
- Scikit-learn/XGBoost: Machine learning algorithms
- Matplotlib/Seaborn: Data visualization
- Google Gen AI: AI/ML capabilities
- LangChain: Language model integration

## Development Conventions

- Python 3.13+ is required
- Frontend uses TypeScript and React
- Docker containerization for consistent deployment
- Separate frontend and backend codebases
- Structured directory organization for data, models, and tests

## Expected Future Implementation

Based on the documentation, the project will likely implement:

- Time-series forecasting models (possibly using Facebook Prophet)
- Anomaly detection algorithms for outbreak detection
- Multi-source data integration (weather, epidemiological, social media)
- Alert mechanisms for outbreak prediction
- Dashboard for data visualization
- Geographic information systems (GIS) for spatial outbreak mapping
