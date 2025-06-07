@echo off
echo Starting Beautiful Captions GUI...
echo.

REM Check if we're in a virtual environment
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Run the GUI
python beautiful_captions_gui.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to exit...
    pause >nul
) 