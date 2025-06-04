@echo off
echo 🎮 PRGAVI Installation Script
echo ============================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo 💡 Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
python --version

:: Check if we're in the right directory
if not exist "shortscreator.py" (
    echo ❌ shortscreator.py not found
    echo 💡 Please run this script from the PRGAVI directory
    pause
    exit /b 1
)

:: Create virtual environment
echo.
echo 🔧 Creating virtual environment...
python -m venv venv

:: Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

:: Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

:: Install requirements
echo 📋 Installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Failed to install dependencies
    echo 💡 Check your internet connection and try again
    pause
    exit /b 1
)

:: Test installation
echo.
echo 🧪 Testing installation...
python shortscreator.py --help

if errorlevel 1 (
    echo ❌ Installation test failed
    pause
    exit /b 1
)

echo.
echo 🎉 Installation completed successfully!
echo.
echo 🚀 Quick Start:
echo    createshortswithcontext.bat "STEAM_URL"
echo.
echo 📖 For more help, see README.md
echo.
pause 