# ML Flow and Workflow for Epidemiology AI

## Overview

This document outlines the machine learning flow and workflow for the Epidemiology AI project, which focuses on early disease outbreak detection and prediction. The system uses time-series analysis and machine learning models to predict outbreak probabilities based on historical patterns combined with real-time data inputs.

## ML Flow Architecture

### 1. Data Collection and Preprocessing

- **Data Sources**: Epidemiological data, climate data, proxy data (pharmacy sales, social media trends), environmental factors
- **Data Pipeline**: Raw data → Cleaning → Feature Engineering → Validation → Storage
- **Data Validation**: Schema validation, outlier detection, missing value handling

### 2. Feature Engineering

- **Temporal Features**: Week of year, seasonal encoding (sin/cos), lag features
- **Weather Features**: Temperature (avg, min, max), precipitation, humidity, rolling averages
- **Historical Features**: Previous case counts (lag 1-4 weeks), rolling averages
- **Environmental Features**: NDVI (Normalized Difference Vegetation Index), dew point, humidity

### 3. Model Training Pipeline

- **Model Selection**: XGBoost, Random Forest (with potential for Prophet for time-series)
- **Cross-Validation**: Time-based splits to prevent data leakage
- **Hyperparameter Tuning**: Grid search or Bayesian optimization
- **Model Evaluation**: MAE, RMSE, R², precision/recall for outbreak detection

### 4. Model Serving

- **API Integration**: FastAPI backend serving the trained model
- **Real-time Predictions**: API endpoints for making predictions on new data
- **Model Monitoring**: Performance tracking, drift detection

## ML Workflow

### Training Workflow

1. **Data Ingestion**: Load historical epidemiological and environmental data
2. **Preprocessing**: Clean data, handle missing values, create features
3. **Model Training**: Train XGBoost model with optimized hyperparameters
4. **Validation**: Evaluate model on holdout test set
5. **Model Serialization**: Save trained model to pickle file
6. **Model Deployment**: Load model into FastAPI service

### Prediction Workflow

1. **Input Validation**: Validate incoming request parameters
2. **Feature Engineering**: Create features from input data (same as training)
3. **Prediction**: Apply trained model to generate prediction
4. **Risk Assessment**: Convert prediction to risk level (Low/Medium/High)
5. **Response**: Return prediction with confidence and risk level

### Model Update Workflow

1. **Trigger**: Scheduled updates or performance degradation detection
2. **Data Refresh**: Incorporate new data into training set
3. **Retraining**: Retrain model with updated data
4. **Validation**: Ensure model performance meets thresholds
5. **Deployment**: Deploy new model version

## Technical Implementation

### Model Architecture

- **Algorithm**: XGBoost Regressor
- **Features**: 33 features including weather, historical cases, seasonal patterns
- **Target**: Weekly dengue case counts
- **Threshold**: Outbreak detection at 75th percentile of historical cases

### API Endpoints

- `/api/v1/predict`: Make outbreak predictions
- `/api/v1/model/stats`: Get model performance statistics
- `/api/v1/model/reload`: Reload model from disk

### Model Persistence

- **Format**: Pickle (.pkl)
- **Location**: `/models/dengue_outbreak_predictor.pkl`
- **Contents**: Trained model, feature columns, threshold, metrics, data source

## Model Validation and Monitoring

### Validation Metrics

- **R² Score**: 0.856 (XGBoost)
- **MAE**: 7.39
- **RMSE**: 11.86
- **Outbreak Detection**: Precision 91.4%, Recall 94.1%

### Monitoring

- **Performance Tracking**: R², MAE, RMSE over time
- **Drift Detection**: Feature distribution changes
- **Alerting**: Performance degradation notifications

## Deployment Strategy

### Local Development

- Jupyter notebooks for model development
- FastAPI for serving
- Docker for containerization

### Production Deployment

- Containerized deployment with Docker Compose
- Model versioning and rollback capabilities
- Health checks and monitoring

## Security Considerations

- Input validation to prevent injection attacks
- Rate limiting for API endpoints
- Secure model loading and validation
