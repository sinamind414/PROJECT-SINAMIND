@echo off
REM start_dev.bat - Khawarizmi Pro Backend (local)
cd /d "%~dp0"
if not exist ".env" (
    echo [ERREUR] .env introuvable
    pause
    exit /b 1
)
docker-compose ps 2>nul | findstr "postgres" >nul
if errorlevel 1 (
    echo [INFO] Demarrage PostgreSQL + Redis...
    docker-compose up -d postgres redis
    timeout /t 3 /nobreak >nul
)
echo [OK] http://localhost:8000
echo [OK] CTRL+C pour arreter
echo.
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause
