@echo off
:: install-hooks.bat — Installation des hooks pre-commit pour Khawarizmi Pro (Windows)
echo === Khawarizmi Pro — Installation Pre-commit ===
echo.

:: Vérifier pre-commit
python -c "import pre_commit" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [1/3] Installation de pre-commit...
    pip install pre-commit
) else (
    echo [1/3] pre-commit deja installe.
)

:: Vérifier ruff
python -c "import ruff" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [2/3] Installation de ruff...
    pip install ruff
) else (
    echo [2/3] ruff deja installe.
)

:: Installer les hooks
echo [3/3] Installation des hooks...
pre-commit install --hook-type pre-commit --hook-type pre-push

echo.
echo === Installation terminee ===
echo.
echo Prochaines etapes :
echo   1. pre-commit run --all-files
echo   2. git add -A
echo   3. pre-commit run --all-files
echo   4. git commit -m "fix: format initial"
echo.
