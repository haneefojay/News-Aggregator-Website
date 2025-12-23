@echo off
echo Starting News Aggregator Services Locally...

:: Check if .env exists
if not exist .env (
    echo .env file not found! Copying .env.example...
    copy .env.example .env
)

:: Start FastAPI in a new window
start "FastAPI - News Aggregator" cmd /k "call .\venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"

:: Start Celery Worker in a new window
start "Celery Worker" cmd /k "call .\venv\Scripts\activate && celery -A app.tasks worker --loglevel=info -P solo"

:: Start Celery Beat in a new window
start "Celery Beat" cmd /k "call .\venv\Scripts\activate && celery -A app.tasks beat --loglevel=info"

echo Services started. 
echo API: http://localhost:8000/docs
echo.
echo Make sure PostgreSQL and Redis are running on your machine!
