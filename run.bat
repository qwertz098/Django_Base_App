@echo off
setlocal

set REPO_URL=https://github.com/qwertz098/Django_Base_App.git
set BRANCH=claude/plan-django-template-PQRYt
set PROJECT_DIR=%~dp0
set VENV_DIR=%PROJECT_DIR%venv
set SRC_DIR=%PROJECT_DIR%src
set REQ_FILE=%PROJECT_DIR%requirements\dev.txt
set ENV_FILE=%PROJECT_DIR%.env
set ENV_EXAMPLE=%PROJECT_DIR%.env.example

echo ========================================
echo  Django Base App - Local Setup
echo ========================================
echo.

:: Clone or pull
if not exist "%PROJECT_DIR%.git" (
    echo [1/6] Cloning repository...
    git clone -b %BRANCH% %REPO_URL% "%PROJECT_DIR%_tmp"
    if errorlevel 1 (
        echo ERROR: git clone failed.
        pause
        exit /b 1
    )
    :: Move contents from temp clone into project dir (bat is already here)
    xcopy /E /Y /Q "%PROJECT_DIR%_tmp\*" "%PROJECT_DIR%" >nul
    rmdir /S /Q "%PROJECT_DIR%_tmp"
) else (
    echo [1/6] Pulling latest changes...
    git -C "%PROJECT_DIR%" pull origin %BRANCH%
    if errorlevel 1 (
        echo ERROR: git pull failed.
        pause
        exit /b 1
    )
)
echo.

:: Create venv if it doesn't exist
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [2/6] Creating virtual environment...
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment. Is Python 3.12 installed?
        pause
        exit /b 1
    )
) else (
    echo [2/6] Virtual environment already exists.
)
echo.

:: Activate venv
call "%VENV_DIR%\Scripts\activate.bat"

:: Install dependencies
echo [3/6] Installing dependencies...
pip install -q -r "%REQ_FILE%"
if errorlevel 1 (
    echo ERROR: pip install failed.
    pause
    exit /b 1
)
echo.

:: Copy .env if missing
if not exist "%ENV_FILE%" (
    echo [4/6] Creating .env from .env.example...
    copy "%ENV_EXAMPLE%" "%ENV_FILE%" >nul
) else (
    echo [4/6] .env already exists.
)
echo.

:: Run migrations
echo [5/6] Running migrations...
python "%SRC_DIR%\manage.py" migrate
if errorlevel 1 (
    echo ERROR: migrations failed.
    pause
    exit /b 1
)
echo.

:: Start server
echo [6/6] Starting development server...
echo.
echo  Server running at http://127.0.0.1:8000
echo  Press Ctrl+C to stop.
echo ========================================
echo.
python "%SRC_DIR%\manage.py" runserver

endlocal
