# API Testing with cURL Commands (Windows CMD)

## Prerequisites

Make sure the server is running: `uvicorn main:app --reload`

---

## 1. Health Endpoints

### Root Endpoint

```cmd
curl http://localhost:8000/
```

### Health Check

```cmd
curl http://localhost:8000/health
```

---

## 2. Authentication Endpoints

### Register User

```cmd
curl -X POST http://localhost:8000/api/v1/auth/register ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"test@example.com\",\"password\":\"testpassword123\",\"full_name\":\"Test User\"}"
```

### Login (Get JWT Token)

```cmd
curl -X POST http://localhost:8000/api/v1/auth/login ^
  -H "Content-Type: application/x-www-form-urlencoded" ^
  -d "username=test@example.com&password=testpassword123"
```

**Save the access_token from the response for protected endpoints!**

### Get Current User (Protected - Requires Token)

Replace `YOUR_TOKEN_HERE` with the token from login:

```cmd
curl http://localhost:8000/api/v1/auth/me ^
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 3. Prediction Endpoints

### Make Prediction

```cmd
curl -X POST http://localhost:8000/api/v1/predict ^
  -H "Content-Type: application/json" ^
  -d "{\"temp_avg\":28.5,\"temp_min\":24.0,\"temp_max\":33.0,\"precipitation_mm\":45.2,\"humidity_percent\":78.5,\"weekofyear\":24,\"previous_cases\":[12,15,18,22]}"
```

---

## 4. Model Endpoints

### Get Model Stats

```cmd
curl http://localhost:8000/api/v1/model/stats
```

### Reload Model

```cmd
curl -X POST http://localhost:8000/api/v1/model/reload
```

---

## 5. Data Ingestion Endpoints

### Ingest Weather Data

```cmd
curl -X POST http://localhost:8000/api/v1/ingest/weather ^
  -H "Content-Type: application/json" ^
  -d "{\"region_id\":1,\"start_date\":\"2024-01-01\",\"end_date\":\"2024-01-31\"}"
```

### Ingest Disease CSV

```cmd
curl -X POST http://localhost:8000/api/v1/ingest/disease ^
  -F "file=@path/to/your/data.csv" ^
  -F "disease_id=1" ^
  -F "region_id=1"
```

### Ingest Google Trends

```cmd
curl -X POST http://localhost:8000/api/v1/ingest/trends ^
  -H "Content-Type: application/json" ^
  -d "{\"keywords\":[\"dengue fever\",\"dengue symptoms\"],\"region\":\"US\",\"region_id\":1,\"timeframe\":\"today 3-m\"}"
```

---

## Quick Test Script (Windows CMD)

Save this as `test_api.bat`:

```batch
@echo off
echo Testing API Endpoints...

echo.
echo 1. Health Check:
curl http://localhost:8000/health

echo.
echo 2. Register User:
curl -X POST http://localhost:8000/api/v1/auth/register -H "Content-Type: application/json" -d "{\"email\":\"test@example.com\",\"password\":\"test123\",\"full_name\":\"Test User\"}"

echo.
echo 3. Login:
curl -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/x-www-form-urlencoded" -d "username=test@example.com&password=test123"

echo.
echo 4. Model Stats:
curl http://localhost:8000/api/v1/model/stats

echo.
echo Done!
```

---

## Notes

- **Line continuation in CMD**: Use `^` at the end of lines
- **Token expiration**: Tokens expire after 30 minutes (configured in settings)
- **File uploads**: Use `-F` flag for multipart/form-data
- **JSON data**: Use `-d` with proper escaping in Windows CMD
- For better JSON formatting in responses, install `jq` or use PowerShell instead
