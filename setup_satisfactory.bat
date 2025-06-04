@echo off
echo Setting up Satisfactory Shorts Creator...
echo This will install all required dependencies and configure ImageMagick.
echo.

:: Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements_satisfactory.txt

:: Configure ImageMagick
echo.
echo Configuring ImageMagick...
python configure_imagemagick.py

echo.
echo Setup complete! You can now run run_satisfactory_shorts.bat to create a Satisfactory shorts video.
echo Press any key to exit...
pause > nul 