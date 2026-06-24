@echo off
setlocal enabledelayedexpansion
set COMPOSE_FILE=%~dp0..\khawarizmi-backend\docker-compose.yml
set PROJECT_DIR=%~dp0..

echo [1/4] Vérification des prérequis...
python --version >nul 2>&1 || (echo ERREUR: Python introuvable & exit /b 1)
docker --version >nul 2>&1 || (echo ERREUR: Docker introuvable & exit /b 1)

if not exist "%PROJECT_DIR%\.env" (
    echo [*] Creation de .env depuis .env.example...
    copy "%PROJECT_DIR%\khawarizmi-backend\.env.example" "%PROJECT_DIR%\.env"
)

echo [2/4] Construction des images Docker...
docker compose -f "%COMPOSE_FILE%" build --pull

echo [3/4] Demarrage des services...
docker compose -f "%COMPOSE_FILE%" up -d

echo [4/4] Verification...
docker compose -f "%COMPOSE_FILE%" ps

echo.
echo Initialisation terminee !
echo Pour voir les logs : scripts\start.bat logs
echo Pour arreter :      scripts\stop.bat
