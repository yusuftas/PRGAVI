@echo off
echo Starting Simple Caption Style Tests...
echo This will create 10 test videos with different caption styles

:: Run the simple caption tests
python create_caption_test_videos.py

echo.
echo If successful, the output videos will be in the output/caption_tests folder.
echo Press any key to exit...
pause > nul 