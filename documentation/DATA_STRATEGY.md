# Epidemiology AI - Data Strategy & Playbook

## 1. Guiding Philosophy

Our data strategy is centered on building a multi-layered, scalable, and reliable data ecosystem. We progress from a validated, static core dataset to a rich, dynamic, multi-source data lake, enabling our models to deliver timely and accurate predictions. Every data source is a strategic asset.

---

## 2. Data Tiers & Acquisition Plan

We classify our data sources into three tiers, representing a phased approach from prototype to a world-class predictive system.

### Tier 1: Core Dataset (MVP & Baseline)

This tier establishes our baseline model performance using a trusted, pre-cleaned academic dataset.

| Data Source           | Type       | Content                                                                                     | Acquisition     | Status       |
| :-------------------- | :--------- | :------------------------------------------------------------------------------------------ | :-------------- | :----------- |
| **DrivenData DengAI** | Static CSV | 20+ years of weekly dengue cases and environmental data for San Juan (sj) and Iquitos (iq). | Manual Download | **Complete** |

- **URL**: [DengAI: Predicting Disease Spread](https://www.drivendata.org/competitions/44/dengai-predicting-disease-spread/)
- **Usage**: Initial model training, feature engineering validation, and baseline performance metrics.

### Tier 2: Essential Augmentation Data (Production Grade)

This tier makes our system operational and responsive by integrating live, real-world data streams.

| Data Source           | Type               | Content                                                                | Acquisition           | Status    |
| :-------------------- | :----------------- | :--------------------------------------------------------------------- | :-------------------- | :-------- |
| **NOAA / IMD**        | Live API           | Real-time and historical weather data (temp, precipitation, humidity). | Automated API Client  | **To-Do** |
| **WHO / ECDC / IDSP** | Live API / Scraper | Official weekly disease case counts for target regions.                | Automated API/Scraper | **To-Do** |

- **Action Item**: Develop scheduled jobs (e.g., via Celery) to ingest and process this data into our database daily/weekly.

### Tier 3: Advanced Proxy Signals (Competitive Edge)

This tier provides the innovative edge, enabling earlier and more nuanced predictions by capturing real-time societal behavior.

| Data Source         | Type          | Content                                                               | Acquisition           | Status     |
| :------------------ | :------------ | :-------------------------------------------------------------------- | :-------------------- | :--------- |
| **Google Trends**   | Live API      | Search interest for keywords like "fever," "dengue symptoms."         | `pytrends` API Client | **To-Do**  |
| **Google Mobility** | Static CSV    | Population movement trends across various categories.                 | Manual / Scheduled DL | **To-Do**  |
| **Twitter API**     | Streaming API | Anonymized public mentions of symptoms (with strict privacy filters). | Stream Processor      | **Future** |

---

## 3. Data Processing & ETL Pipeline

Our ETL (Extract, Transform, Load) pipeline is designed for robustness and consistency.

1.  **Extract**: Data is acquired from sources via API clients, scrapers, or manual uploads.
2.  **Validate**: Incoming data is validated against Pydantic schemas. Invalid or corrupt data is flagged and logged.
3.  **Clean & Normalize**:
    - **Missing Values**: Handled using strategic forward-fill (`ffill`) and backward-fill (`bfill`) to respect time-series integrity.
    - **Unit Conversion**: Standardize all units (e.g., Kelvin to Celsius).
    - **Outlier Detection**: Apply statistical methods to flag and handle anomalous readings.
4.  **Feature Engineering**: The cleaned data is enriched with predictive features (e.g., lag variables, rolling averages, seasonal encoding).
5.  **Load**: The processed, feature-rich data is loaded into the appropriate PostgreSQL/TimescaleDB tables for use by the ML models and frontend.

---

## 4. Data Governance & Quality

- **Data Privacy**: We operate on a "privacy-by-design" principle. All proxy signals (Tier 3) will be aggregated and anonymized, with no Personally Identifiable Information (PII) ever being stored.
- **Security**: API keys and database credentials are managed securely via environment variables and are never hard-coded.
- **Data Lineage**: All data loaded into the system will have clear source attribution, ensuring we can trace any data point back to its origin.
- **Directory Structure**: We maintain a strict and clean data hierarchy to ensure reproducibility.
  ```
  data/
  ├── raw/          # Original, immutable data from sources
  ├── processed/    # Cleaned, transformed, and feature-enriched data
  └── analysis/     # Notebooks, reports, and visualizations
  ```

---

## 5. Target Schema & Storage

- **Time-Series Data**: `outbreak_data` and `environmental_data` are stored in **TimescaleDB hypertables**, optimized for high-speed time-series queries.
- **Structured Data**: `users`, `diseases`, `geographic_regions` are stored in standard PostgreSQL tables.
- **ML Metadata**: `predictions`, `model_versions`, and `alerts` are stored in PostgreSQL to track model performance and system activity.
