@echo off
set COMPOSE_FILE=%~dp0..\khawarizmi-backend\docker-compose.yml

echo Arret des services...
docker compose -f "%COMPOSE_FILE%" down

echo.
echo Services arretes.
