@echo off
REM Quick setup script for backend to resolve 500 Internal Server Error during login

echo Checking if backend is in the correct directory...
if not exist "backend\." (
    echo Error: This script must be run from the project root directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

echo.
echo Step 1: Installing backend dependencies...
cd backend
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
)

pip install -r requirements.txt

echo.
echo Step 2: Setting up local SQLite database for testing...
REM Backup original .env if it exists
if exist ".env" (
    copy .env .env.backup > nul
    echo Backed up original .env to .env.backup
)

REM Create a local development .env file
echo # Local Development Environment > .env
echo DATABASE_URL=sqlite:///./todo_app_local.db >> .env
echo JWT_SECRET_KEY=local-development-secret-key-for-testing >> .env
echo JWT_ALGORITHM=HS256 >> .env
echo JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30 >> .env
echo.
echo Created local .env file with SQLite database configuration

echo.
echo Step 3: Creating database tables...
python create_tables.py

echo.
echo Step 4: Starting backend server...
echo Please keep this window open and start the frontend in a new terminal
echo.
echo To start the frontend:
echo   1. Open a new terminal/command prompt
echo   2. Navigate to this project directory
echo   3. cd frontend
echo   4. npm install
echo   5. npm run dev
echo.
echo The backend will be available at http://localhost:8000
echo The frontend will be available at http://localhost:3000

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000