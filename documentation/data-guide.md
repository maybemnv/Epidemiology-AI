# Data Acquisition Guide

This guide provides detailed information on acquiring datasets for the Epidemiology AI project.

## Overview

The project requires multiple data sources to build an effective outbreak prediction system:

1. **Disease Case Data** (dengue, malaria, flu, etc.)
2. **Weather/Climate Data** (temperature, rainfall, humidity)
3. **Social Media/Search Trends** (optional)
4. **Pharmacy Sales Data** (optional/synthetic)

## Primary Data Sources

### 1. Disease Outbreak Data

#### DrivenData - Dengue Fever Prediction Dataset

**Best Option for Getting Started**

- **URL**: https://www.drivendata.org/competitions/44/dengai-predicting-disease-spread/
- **What it contains**:
  - Weekly dengue cases for San Juan, Puerto Rico and Iquitos, Peru
  - 20+ years of historical data
  - Pre-aligned with weather data
- **Format**: CSV files
- **How to get**:
  1. Create free account at DrivenData.org
  2. Navigate to "DengAI: Predicting Disease Spread" competition
  3. Download `dengue_features_train.csv` and `dengue_labels_train.csv`
  4. Place in `data/raw/` folder

#### WHO Disease Outbreak News

- **URL**: https://www.who.int/emergencies/disease-outbreak-news
- **Format**: Reports and bulletins (requires scraping/manual extraction)
- **Use**: Supplementary validation data

#### India - IDSP (Integrated Disease Surveillance Programme)

- **URL**: https://idsp.mohfw.gov.in/
- **Access**: Some data publicly available, detailed data requires permissions
- **Alternative**: Use state health department bulletins

### 2. Weather Data

#### NOAA Climate Data Online

**Recommended for Global Coverage**

- **URL**: https://www.ncdc.noaa.gov/cdo-web/
- **What it contains**:
  - Temperature (min, max, average)
  - Precipitation
  - Humidity
  - Wind speed
- **How to get**:
  1. Visit the Climate Data Online portal
  2. Select dataset: "Global Summary of the Day" (GSOD)
  3. Choose location and date range
  4. Request data (free, delivered via email)
  5. Save to `data/raw/weather/`

#### India Meteorological Department (IMD)

- **URL**: https://www.imd.gov.in/
- **Data Products Page**: https://www.imd.gov.in/pages/main.php
- **Access**: Some data freely available, historical data may require request

#### OpenWeatherMap API (Alternative)

- **URL**: https://openweathermap.org/api
- **Free tier**: 1000 calls/day
- **Good for**: Recent/current weather data
- **Historical data**: Requires paid plan

### 3. Google Trends Data (Optional)

- **URL**: https://trends.google.com/trends
- **How to use**:
  1. Search for terms like "dengue fever symptoms", "mosquito bites", "fever clinic"
  2. Set location (e.g., India, specific state)
  3. Download CSV for desired time period
  4. Save to `data/raw/search_trends/`

- **Python library**: `pytrends`
  ```bash
  pip install pytrends
  ```

### 4. Synthetic/Example Data

If you cannot access real data immediately, you can:

1. **Use the prototype's synthetic data generator** (included in notebook)
2. **Kaggle datasets**:
   - Search "dengue dataset" or "disease outbreak"
   - https://www.kaggle.com/datasets

## Data Directory Structure

Organize your data as follows:

```
data/
├── raw/                    # Original, immutable data
│   ├── dengue/
│   │   ├── dengue_features_train.csv
│   │   └── dengue_labels_train.csv
│   ├── weather/
│   │   └── noaa_gsod_data.csv
│   └── search_trends/
│       └── google_trends_dengue.csv
├── processed/              # Cleaned, transformed data
│   └── combined_features.csv
└── models/                 # Saved ML models
    └── outbreak_predictor.pkl
```

## Quick Start: Download Sample Data

For immediate prototyping, use the DrivenData dengue dataset:

### Step-by-Step:

1. **Visit**: https://www.drivendata.org/competitions/44/dengai-predicting-disease-spread/data/

2. **Download these files**:
   - `dengue_features_train.csv` - Weather and vegetation data
   - `dengue_labels_train.csv` - Dengue case counts

3. **Create directory**:

   ```bash
   mkdir -p "d:\Projects\Epidemiology AI\data\raw\dengue"
   ```

4. **Move files** to `data/raw/dengue/`

5. **Verify**:
   ```bash
   ls data/raw/dengue/
   # Should show: dengue_features_train.csv, dengue_labels_train.csv
   ```

## Data Preprocessing

The prototype notebook (`notebooks/dengue_outbreak_prediction.ipynb`) includes:

- Automated data loading
- Missing value handling
- Feature engineering
- Train/test splitting

## Alternative: Generate Synthetic Data

If you want to test the system without downloading data, the prototype includes a synthetic data generator:

```python
from prototype_demo import generate_synthetic_data
synthetic_data = generate_synthetic_data(days=365*3)  # 3 years of data
```

## Next Steps

After acquiring data:

1. Follow the [Setup Guide](setup-guide.md) for environment configuration
2. Run the [Prototype Notebook](../notebooks/dengue_outbreak_prediction.ipynb)
3. Experiment with different models and features

## Troubleshooting

### "Cannot access DrivenData"

- Use Kaggle as alternative: search "dengue prediction dataset"
- Or use the synthetic data generator in the prototype

### "Weather data doesn't match disease data dates"

- Use pandas date merging with `how='outer'` to align datasets
- Interpolate missing weather values

### "Data is too large"

- Start with 2-3 years of data
- Use `pandas.read_csv(chunksize=1000)` for large files

## Resources

- [DrivenData Competition Forum](https://community.drivendata.org/)
- [NOAA Climate Data Guide](https://www.ncdc.noaa.gov/cdo-web/search)
- [Pandas Time Series Documentation](https://pandas.pydata.org/docs/user_guide/timeseries.html)
