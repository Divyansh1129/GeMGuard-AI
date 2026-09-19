@echo off
TITLE GeMGuard AI — One-Command Setup
echo ============================================================
echo   GeMGuard AI — Automated Setup & Demo Initializer
echo ============================================================
echo.

echo [1/4] Installing Python dependencies...
python -m pip install -r Backend\requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Python dependencies.
    pause
    exit /b %errorlevel%
)

echo [2/4] Running test suite...
python -m pytest Backend\tests\ -v --tb=short
if %errorlevel% neq 0 (
    echo [WARNING] Some tests failed. Check output above.
)

echo [3/4] Seeding demo database (3 scenario bidders + sample tender)...
python scripts\seed_demo.py
if %errorlevel% neq 0 (
    echo [ERROR] Failed to seed demo database.
    pause
    exit /b %errorlevel%
)

echo [4/4] Setup completed successfully!
echo.
echo ============================================================
echo   TO RUN THE PLATFORM:
echo   1. Start Backend:  uvicorn app.main:app --reload --port 8000 (in Backend\)
echo   2. Start Frontend: npm run dev (in Frontend\)
echo ============================================================
echo.
pause
