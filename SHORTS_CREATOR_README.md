# Shorts Creator

A unified tool to create professional short-form gaming videos with AI narration and captions for any Steam game.

## Features

- ✅ Creates 9:16 format videos perfect for TikTok, YouTube Shorts, and Instagram Reels
- ✅ High-quality AI narration using Chatterbox TTS
- ✅ Automatic caption generation with word highlighting
- ✅ Ken Burns effect for image transitions
- ✅ Split-screen format with gameplay video at bottom
- ✅ Optimized for gaming content
- ✅ **Automatic Steam page content scraping** (screenshots, videos, description)

## Prerequisites

- Python 3.8 or higher
- ImageMagick 7.1.1-47 (required for captions)
- Internet connection (for Steam page scraping)

## Installation

1. **Setup environment**:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```
   
   Or use the setup batch file:
   ```
   setup.bat
   ```

3. **Configure ImageMagick**: 
   ```
   python configure_imagemagick.py
   ```
   
   Default installation path: C:\Program Files\ImageMagick-7.1.1-Q16-HDRI

## Quick Start

### Option 1: Automatic Steam Game Download

The easiest way to create a video is to use the automatic Steam scraper:

```
python shortscreator.py --steam-url "https://store.steampowered.com/app/GAME_ID/GAME_NAME/"
```

This will:
1. Download screenshots and trailer video from the Steam page
2. Extract game information (description, features, etc.)
3. Generate a script based on the game content with the SHORTS_VIDEO_GUIDELINES.md
4. Create a professional shorts video

### Option 2: Use Batch File for Common Games

```
run_custom_game.bat in RunGameBat 
```

This interactive script will prompt you for:
- Game name
- Steam URL (optional)
- Custom features (optional)

## Steam Scraping

The tool includes a powerful Steam page scraper that can automatically download:

- Game screenshots (up to 12 high-quality images)
- Trailer videos
- Game description and features
- Developer information

To use it:

```
python shortscreator.py --steam-url "https://store.steampowered.com/app/GAME_ID/GAME_NAME/"
```

Or for more control:

```
python steam_page_scraper.py --url "https://store.steampowered.com/app/GAME_ID/GAME_NAME/" --output-dir "downloads/game_name"
```

## Advanced Usage

You can run the script directly with custom parameters:

```
python shortscreator.py --game "Game Name" --images "path/to/images" --video "path/to/video.mp4"
```

### Command Line Arguments

- `--game`: Game name
- `--steam-url`: Steam store URL (for automatic content scraping)
- `--images`: Path to images directory (if not using Steam scraping)
- `--video`: Path to video file (if not using Steam scraping)
- `--output`: Output directory (default: "output")
- `--features`: Comma-separated game features
- `--script`: Custom script (if not provided, one will be generated)
- `--exaggeration`: Voice exaggeration level from 0.0-1.0 (default: 0.6)

## Examples

### Example 1: Create video for any game using Steam URL

```
python shortscreator.py --steam-url "https://store.steampowered.com/app/526870/Satisfactory/"
```

### Example 2: Create video with custom assets

```
python shortscreator.py --game "Cyberpunk 2077" --images "downloads/cyberpunk_images" --video "downloads/cyberpunk_trailer.mp4" --features "immersive open world,customizable character,futuristic technology"
```

### Example 3: Create video with custom script

```
python shortscreator.py --game "Elden Ring" --steam-url "https://store.steampowered.com/app/1245620/ELDEN_RING/" --script "path/to/custom_script.txt"
```

## Output

The script will create a file in the output directory with the format `game_name_shorts.mp4`.

For example, running with `--game "Elden Ring"` will create:
```
output/elden_ring_shorts.mp4
```

## Troubleshooting

1. **ImageMagick issues**: If captions aren't working, make sure ImageMagick is properly installed and configured. Run `setup_imagemagick.py` again.

2. **Steam scraping issues**: If the scraper can't download content, try:
   - Check your internet connection
   - Verify the Steam URL is correct
   - Some games may have age verification - the scraper attempts to bypass this but may not always succeed

3. **GPU/CPU issues**: By default, the script will use GPU if available. If you encounter CUDA issues, run the CPU version:
   ```
   run_shortscreator_cpu.bat
   ```

4. **Missing dependencies**: The script will attempt to install missing dependencies automatically, but you may need to install them manually:
   ```
   pip install -r requirements.txt
   ```

## Requirements

The video creation process needs:
- At least 6 high-quality images (downloaded automatically if using Steam scraper)
- A gameplay video clip (downloaded automatically if using Steam scraper)
- Approximately 500MB of free disk space
- 4GB+ of RAM

## Technical Details

- Video Resolution: 1080x1920 (9:16)
- Video Codec: H.264
- Audio Codec: AAC
- Framerate: 30fps
- Target Duration: 45-50 seconds
- Script Length: 180-200 words 