@echo off
echo Starting Shorts Creator with Chatterbox TTS and Captions (CPU mode)...
echo This will create a shorts-style video for Tainted Grail

set MAGICK_HOME=C:\Program Files\ImageMagick-7.1.1-Q16-HDRI
set PATH=%MAGICK_HOME%;%PATH%

:: Force CPU mode and use slower TTS voice
set CUDA_VISIBLE_DEVICES=-1
set TORCH_DEVICE=cpu

:: Run with slower TTS voice by reducing exaggeration
python shortscreator.py --game "Tainted Grail" ^
  --images "downloads/tainted_grail_manual" ^
  --video "downloads/tainted_grail_videos/tainted_grail_trailer_1.mp4" ^
  --output "output" ^
  --features "epic Arthurian legends,limitless character builds,massive exploration zones" ^
  --exaggeration 0.3

echo.
echo If successful, the output video will be in the output folder.
echo Press any key to exit...
pause > nul 