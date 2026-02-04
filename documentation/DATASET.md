# Dataset Documentation for Epidemiology AI

## Dataset Overview

The Epidemiology AI project uses the **DrivenData DengAI: Predicting Disease Spread** dataset, which contains epidemiological and environmental data for dengue fever prediction. The dataset focuses on two locations: San Juan (sj) and Iquitos (iq).

## Data Sources

- **Competition**: DrivenData DengAI Competition
- **URL**: https://www.drivendata.org/competitions/44/dengai-predicting-disease-spread/
- **Target Variable**: Weekly dengue case counts

## Dataset Structure

### Training Data

- **dengue_features_train.csv**: Environmental and temporal features
- **dengue_labels_train.csv**: Weekly case counts (target variable)

### Feature Categories

#### 1. Temporal Features

- `city`: Location identifier (sj = San Juan, iq = Iquitos)
- `year`: Year of observation
- `weekofyear`: Week number (1-52)
- `week_start_date`: Start date of the week

#### 2. Vegetation Indices

- `ndvi_ne`: Normalized Difference Vegetation Index (Northeast)
- `ndvi_nw`: Normalized Difference Vegetation Index (Northwest)
- `ndvi_se`: Normalized Difference Vegetation Index (Southeast)
- `ndvi_sw`: Normalized Difference Vegetation Index (Southwest)

#### 3. Weather Features

- `precipitation_amt_mm`: Precipitation amount in millimeters
- `reanalysis_sat_precip_amt_mm`: Reanalysis satellite precipitation
- `station_precip_mm`: Station precipitation measurement

#### 4. Temperature Features

- `reanalysis_air_temp_k`: Reanalysis air temperature (Kelvin)
- `reanalysis_avg_temp_k`: Reanalysis average temperature (Kelvin)
- `reanalysis_dew_point_temp_k`: Reanalysis dew point temperature (Kelvin)
- `reanalysis_max_air_temp_k`: Reanalysis maximum air temperature (Kelvin)
- `reanalysis_min_air_temp_k`: Reanalysis minimum air temperature (Kelvin)
- `reanalysis_tdtr_k`: Reanalysis diurnal temperature range (Kelvin)
- `station_avg_temp_c`: Station average temperature (Celsius)
- `station_diur_temp_rng_c`: Station diurnal temperature range (Celsius)
- `station_max_temp_c`: Station maximum temperature (Celsius)
- `station_min_temp_c`: Station minimum temperature (Celsius)

#### 5. Humidity Features

- `reanalysis_relative_humidity_percent`: Reanalysis relative humidity (%)
- `reanalysis_specific_humidity_g_per_kg`: Reanalysis specific humidity (g/kg)

## Data Characteristics

### San Juan (sj) Data

- **Time Period**: 1990-04-30 to 2008-04-22
- **Samples**: 936 weeks
- **Location**: San Juan, Puerto Rico

### Iquitos (iq) Data

- **Time Period**: 1997-06-03 to 2008-04-22
- **Samples**: 520 weeks
- **Location**: Iquitos, Peru

## Data Preprocessing

### Missing Value Handling

- Forward fill (ffill) and backward fill (bfill) for missing values
- Missing values were present in vegetation indices and some weather features

### Feature Engineering

- **Temperature Conversion**: Kelvin to Celsius conversion for temperature features
- **Lag Features**: Previous case counts (1-4 weeks prior)
- **Rolling Averages**: 2-week and 4-week rolling averages for weather features
- **Seasonal Encoding**: Sine and cosine transformations of week of year

### Derived Features

- `temp_avg`: Average temperature (converted from Kelvin)
- `temp_min`: Minimum temperature (converted from Kelvin)
- `temp_max`: Maximum temperature (converted from Kelvin)
- `precipitation_mm`: Precipitation amount
- `humidity_percent`: Relative humidity percentage
- `cases_lag_1` to `cases_lag_4`: Lagged case counts
- `temp_avg_roll_2w`, `temp_avg_roll_4w`: Rolling temperature averages
- `precip_roll_2w`, `precip_roll_4w`: Rolling precipitation averages
- `humidity_roll_2w`, `humidity_roll_4w`: Rolling humidity averages
- `week_sin`, `week_cos`: Seasonal encoding

## Target Variable

- `total_cases`: Weekly dengue case counts (integer)
- **Summary Statistics**:
  - Count: 1456 samples
  - Mean: 34.18 cases
  - Standard Deviation: 51.38 cases
  - Min: 0 cases
  - Max: 461 cases
  - 25th Percentile: 9 cases
  - 50th Percentile (Median): 19 cases
  - 75th Percentile: 37 cases

## Data Quality Considerations

- Missing values were handled using forward/backward fill
- Outlier detection and handling may be needed for extreme weather or case count values
- Temporal consistency maintained in time series structure

## Feature Importance

Based on XGBoost model analysis:

1. `cases_lag_1` (0.858 importance)
2. `humidity_roll_4w` (0.020 importance)
3. `cases_lag_2` (0.019 importance)
4. `humidity_roll_2w` (0.009 importance)
5. `cases_lag_3` (0.009 importance)

## Data Limitations

- Limited to two geographic locations (San Juan and Iquitos)
- Historical data may not reflect current conditions
- Missing data in vegetation indices
- Potential climate and environmental changes over the time period

## Usage in ML Pipeline

- Training features: 33 engineered features
- Target: Weekly case counts
- Time-based train/test split to prevent data leakage
- Outbreak threshold defined at 75th percentile of historical cases (39.0 cases)
