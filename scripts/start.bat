@echo off
set COMPOSE_FILE=%~dp0..\khawarizmi-backend\docker-compose.yml

if /I "%1"=="logs" (
    echo Suivi des logs (Ctrl+C pour quitter)...
    docker compose -f "%COMPOSE_FILE%" logs -f
) else (
    echo Demarrage des services en arriere-plan...
    docker compose -f "%COMPOSE_FILE%" up -d
    echo.
    echo Services demarres.
    echo Pour voir les logs : scripts\start.bat logs
)
