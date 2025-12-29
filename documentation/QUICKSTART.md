# Quick Start Guide

## For Hackathon Judges/Reviewers

This project is an **AI-powered Disease Outbreak Early Warning System** for predicting dengue outbreaks.

## 🚀 Fastest Path to See the Demo

### Option 1: Jupyter Notebook (Recommended)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch Jupyter
jupyter notebook

# 3. Open and run the notebook
# Navigate to: notebooks/dengue_outbreak_prediction.ipynb
# Click "Cell" → "Run All"
```

**The notebook includes:**

- Synthetic data generation (no downloads needed!)
- Complete ML pipeline
- Visualizations
- Model training (Random Forest & XGBoost)
- Outbreak detection system

### Option 2: FastAPI Backend

```bash
# 1. Install dependencies (if not done)
pip install -r requirements.txt

# 2. Start the API server
cd src
uvicorn main:app --reload

# 3. Open interactive API docs
# Visit: http://localhost:8000/docs
```

### Option 3: Quick Overview

```bash
# Just run the main entry point
python main.py
```

## 📁 What's Included

### Documentation (in `documentation/` folder)

- **data-guide.md** - Where to get real dengue & weather data
- **setup-guide.md** - Complete installation & troubleshooting
- **Problem statement.md** - Original problem description
- Plus 10+ other design documents

### Working Prototype

- **notebooks/dengue_outbreak_prediction.ipynb** - Full ML pipeline
  - Loads data (real or synthetic)
  - Feature engineering
  - Trains multiple models
  - Visualizes predictions
  - Detects outbreaks

### Backend API

- **src/main.py** - FastAPI application
- **src/api/routes.py** - API endpoints
- **src/models/predictor.py** - ML model wrapper

## 🎯 Key Features Demonstrated

1. **Multi-source Data Integration** - Weather + Disease cases
2. **ML-based Prediction** - Random Forest & XGBoost models
3. **Early Warning System** - Outbreak risk classification
4. **Feature Engineering** - Lag features & rolling averages
5. **Visualization** - Time series plots & correlations

## 💡 For Real Deployment

The system is designed to integrate:

- Real-time weather APIs
- Health surveillance data
- Google Trends (search patterns)
- Pharmacy sales data

## 📊 Expected Results

When running the notebook, you'll see:

- **R² Score**: ~0.70-0.85 (varies with synthetic data)
- **MAE**: ~5-10 cases per week
- **Outbreak Detection**: ~80%+ precision

## 🔗 Repository Structure

```
├── documentation/       # All project docs
├── notebooks/          # Jupyter prototype
├── src/               # Backend code
│   ├── main.py       # FastAPI app
│   ├── api/          # API routes
│   └── models/       # ML predictor
├── frontend/          # React app (structure)
├── data/             # Data storage
├── main.py           # Entry point
└── requirements.txt  # Dependencies
```

## ⏱️ Time Estimates

- **View demo**: 5 minutes (run notebook)
- **Understand approach**: 15 minutes (read docs + run prototype)
- **Full exploration**: 30 minutes (review all code + docs)

## 🤝 Questions?

Check the documentation folder for detailed guides on:

- Data acquisition
- System architecture
- Technical specifications
- Timeline & milestones

---

**Built for**: Epidemiology AI Hackathon  
**Tech Stack**: Python, FastAPI, scikit-learn, XGBoost, React  
**Status**: Prototype with full technical design
