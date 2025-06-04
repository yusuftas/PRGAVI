@echo off
setlocal EnableDelayedExpansion

:: ===============================================
:: CREATE SHORTS WITH CONTEXT
:: Automated batch script for shortscreator.py
:: ===============================================

echo.
echo 🎮 CREATE SHORTS WITH CONTEXT
echo ==========================================
echo.

:: Check if at least Steam URL is provided
if "%~1"=="" (
    echo ❌ Error: Steam URL is required!
    echo.
    echo 💡 Usage:
    echo    createshortswithcontext.bat "STEAM_URL" ["SCRIPT_TEXT"]
    echo.
    echo 📝 Examples:
    echo    createshortswithcontext.bat "https://store.steampowered.com/app/2622380/ELDEN_RING_NIGHTREIGN/"
    echo    createshortswithcontext.bat "https://store.steampowered.com/app/275850/No_Mans_Sky/" "Custom script here..."
    echo.
    pause
    exit /b 1
)

:: Extract game name from Steam URL
set "STEAM_URL=%~1"
echo 🔗 Steam URL: %STEAM_URL%

:: Extract App ID from URL
for /f "tokens=2 delims=/" %%a in ("%STEAM_URL%") do (
    for /f "tokens=1 delims=/" %%b in ("%%a") do (
        if "%%b"=="app" (
            for /f "tokens=3 delims=/" %%c in ("%STEAM_URL%") do (
                set "APP_ID=%%c"
            )
        )
    )
)

if "!APP_ID!"=="" (
    echo ❌ Error: Could not extract App ID from Steam URL
    echo 💡 Make sure URL is in format: https://store.steampowered.com/app/APPID/GAMENAME/
    pause
    exit /b 1
)

echo 🎯 App ID: !APP_ID!

:: Get game name from Steam API
echo 🔄 Fetching game info from Steam...
powershell -Command "try { $response = Invoke-RestMethod -Uri 'https://store.steampowered.com/api/appdetails?appids=!APP_ID!' -ErrorAction Stop; if ($response.'!APP_ID!'.success) { $response.'!APP_ID!'.data.name } else { 'Unknown Game' } } catch { 'Unknown Game' }" > temp_game_name.txt

set /p GAME_NAME=<temp_game_name.txt
del temp_game_name.txt

if "!GAME_NAME!"=="Unknown Game" (
    echo ⚠️ Warning: Could not fetch game name from Steam API
    set /p GAME_NAME="Please enter the game name manually: "
)

echo 🎮 Game: !GAME_NAME!
echo.

:: Check if script is provided as second parameter
set "PROVIDED_SCRIPT=%~2"

if "!PROVIDED_SCRIPT!"=="" (
    echo 📝 No script provided - will use interactive script creation
    echo 💡 You'll be prompted to enter a custom script or use auto-generated one
    echo.
    set "SCRIPT_MODE=interactive"
) else (
    echo 📝 Script provided: "!PROVIDED_SCRIPT!"
    echo 💾 Saving script to temporary file...
    echo !PROVIDED_SCRIPT! > temp_script.txt
    set "SCRIPT_MODE=provided"
    echo.
)

:: Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo 🔧 Activating virtual environment...
    call venv\Scripts\activate.bat
    echo ✅ Virtual environment activated
    echo.
)

:: Check if shortscreator.py exists
if not exist "shortscreator.py" (
    echo ❌ Error: shortscreator.py not found in current directory
    echo 💡 Make sure you're running this from the Project GameVids directory
    pause
    exit /b 1
)

:: Prepare Python command
if "!SCRIPT_MODE!"=="provided" (
    echo 🚀 Running shortscreator with provided script...
    echo ⚠️ Note: Custom script injection will be handled by pre-saving it
    echo.
    
    :: Create a temporary game folder and script
    set "SAFE_NAME=!GAME_NAME: =_!"
    set "SAFE_NAME=!SAFE_NAME:-=_!"
    
    :: Convert to lowercase (simplified)
    for %%i in (A B C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
        set "SAFE_NAME=!SAFE_NAME:%%i=%%i!"
    )
    
    mkdir "games\!SAFE_NAME!" 2>nul
    
    :: Create script.json with provided script
    echo { > "games\!SAFE_NAME!\script.json"
    echo   "game_name": "!GAME_NAME!", >> "games\!SAFE_NAME!\script.json"
    echo   "script": "!PROVIDED_SCRIPT!", >> "games\!SAFE_NAME!\script.json"
    echo   "script_type": "user_provided", >> "games\!SAFE_NAME!\script.json"
    echo   "created_date": "!date! !time!", >> "games\!SAFE_NAME!\script.json"
    echo   "word_count": 0, >> "games\!SAFE_NAME!\script.json"
    echo   "estimated_duration": 0 >> "games\!SAFE_NAME!\script.json"
    echo } >> "games\!SAFE_NAME!\script.json"
    
    :: Create script.txt
    echo !PROVIDED_SCRIPT! > "games\!SAFE_NAME!\script.txt"
    
    echo ✅ Pre-saved custom script to games\!SAFE_NAME!\
    echo.
    
    :: Run with no-input flag since script is pre-saved
    python shortscreator.py --game "!GAME_NAME!" --steam-url "!STEAM_URL!" --no-input
) else (
    echo 🚀 Running shortscreator with interactive script creation...
    echo 💡 You'll be prompted to enter your script or use auto-generated
    echo.
    
    :: Run with interactive mode (default)
    python shortscreator.py --game "!GAME_NAME!" --steam-url "!STEAM_URL!"
)

:: Check if Python command was successful
if !ERRORLEVEL! EQU 0 (
    echo.
    echo 🎉 SUCCESS! Shorts video created successfully!
    echo.
    echo 📁 Check the output folder for your video:
    dir /b output\*.mp4 | findstr /i "!SAFE_NAME!" 2>nul
    echo.
    echo 📊 View catalog:
    python shortscreator.py --catalog
    echo.
    
    :: Ask if user wants to open output folder
    set /p OPEN_FOLDER="🔍 Open output folder? (y/N): "
    if /i "!OPEN_FOLDER!"=="y" (
        explorer output
    )
    
    :: Ask if user wants to view the video
    set /p PLAY_VIDEO="▶️ Play the created video? (y/N): "
    if /i "!PLAY_VIDEO!"=="y" (
        for %%f in (output\*!SAFE_NAME!*.mp4) do (
            start "" "%%f"
            goto :video_opened
        )
        echo ❌ Video file not found
        :video_opened
    )
) else (
    echo.
    echo ❌ ERROR: Shorts creation failed!
    echo 💡 Check the error messages above for details
)

:: Cleanup temporary files
if exist "temp_script.txt" del temp_script.txt
if exist "temp_game_name.txt" del temp_game_name.txt

echo.
echo 🏁 Process completed!
pause 