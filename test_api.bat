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
