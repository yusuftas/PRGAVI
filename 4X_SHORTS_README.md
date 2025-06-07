# 4X Strategy Game Shorts Creator

## Overview

The `createshortsfor4x.bat` and `shortscreatorfor4x.py` scripts are specialized versions of the original shorts creator, designed specifically for **turn-based 4X strategy games**. The key difference is that these scripts **preserve all visual content** by using black bands instead of zooming/cropping.

## Why This Version?

### Problem with Standard Shorts for 4X Games
- **Information Loss**: Standard shorts creators crop/zoom images to fit the 9:16 aspect ratio
- **Strategic Elements Hidden**: Critical UI elements, maps, and strategic information get cut off
- **Context Missing**: Turn-based strategy games rely on seeing the full game state

### 4X Version Solution
- **No Zoom/Crop**: Images and videos are resized to fit completely within the frame
- **Black Bands**: Letterboxing (black bars) is added to maintain original aspect ratios
- **Full Visibility**: Every pixel of strategic information remains visible
- **Better for Strategy**: Viewers can see complete maps, UI elements, and game states

## Key Features

### 🎯 No Zoom Strategy
- Images are scaled down to fit entirely within the vertical video format
- Black bands fill empty space (like watching a widescreen movie on TV)
- No strategic information is lost to cropping

### 🎮 4X Game Optimized
- Perfect for Civilization, Crusader Kings, Europa Universalis, etc.
- Preserves complex UI elements and strategic overlays
- Maintains map readability and strategic context

### 📊 Separate Catalog
- Uses `game_catalog_4x.json` to track 4X strategy game videos
- Different processing settings optimized for strategy content
- Specialized metadata for turn-based games

## Usage

### Basic Usage
```batch
createshortsfor4x.bat "https://store.steampowered.com/app/289070/Sid_Meiers_Civilization_VI/"
```

### With Custom Script
```batch
createshortsfor4x.bat "STEAM_URL" "Explore the vast strategic depth of this 4X masterpiece..."
```

### Examples of Perfect 4X Games
- **Civilization VI**: `https://store.steampowered.com/app/289070/Sid_Meiers_Civilization_VI/`
- **Crusader Kings III**: `https://store.steampowered.com/app/1158310/Crusader_Kings_III/`
- **Europa Universalis IV**: `https://store.steampowered.com/app/236850/Europa_Universalis_IV/`
- **Stellaris**: `https://store.steampowered.com/app/281990/Stellaris/`
- **Total War: Warhammer III**: `https://store.steampowered.com/app/1142710/Total_War_WARHAMMER_III/`

## Technical Differences

### Image Processing
```python
# Original: Crops to fit
img_clip = img_clip.crop(x1=x1, x2=x2)

# 4X Version: Scales with black bands
processed_image = resize_with_black_bands(pil_image, width, height)
```

### Video Processing
```python
# Original: Crops video to fit
video_clip = video_clip.crop(x1=x1, x2=x2)

# 4X Version: Centers video with black bands
video_clip = video_clip.set_position(('center', y_offset))
```

## File Structure

```
Project GameVids/
├── createshortsfor4x.bat          # 4X batch script
├── shortscreatorfor4x.py          # 4X Python script
├── createwithbeatifulcaptions.bat # Original batch script
├── shortscreatorwithbeautifulcaptions.py # Original Python script
├── catalog/
│   ├── game_catalog.json          # Original catalog
│   └── game_catalog_4x.json       # 4X strategy catalog
└── output/
    ├── *_shorts.mp4               # Original format videos
    └── *_4x_shorts.mp4            # 4X format videos
```

## When to Use Each Version

### Use `createshortsfor4x.bat` for:
- ✅ Turn-based strategy games (4X, Grand Strategy)
- ✅ Games with complex UI that needs to be fully visible
- ✅ Map-based games where geography is important
- ✅ Games where strategic information is spread across the screen
- ✅ When you want to preserve ALL visual information

### Use `createwithbeatifulcaptions.bat` for:
- ✅ Action games with focused central action
- ✅ Adventure games with cinematic scenes
- ✅ Games where cropping enhances focus
- ✅ Content where dramatic zooming improves engagement

## Script Content Suggestions

### Good 4X Script Themes
- **Empire Building**: "Watch civilizations rise from humble settlements to vast empires..."
- **Strategic Depth**: "Every decision shapes the fate of nations in this complex strategy masterpiece..."
- **Diplomatic Intrigue**: "Navigate the treacherous waters of international diplomacy..."
- **Technological Progress**: "Guide your civilization through ages of discovery and innovation..."

### Script Length
- Target: 30-60 seconds (150-300 words)
- Focus on strategic elements rather than action
- Emphasize depth, complexity, and long-term thinking

## Output Differences

### Standard Version Output
- Filename: `{game_name}_shorts.mp4`
- Format: Cropped/zoomed content
- Best for: Action-focused content

### 4X Version Output  
- Filename: `{game_name}_4x_shorts.mp4`
- Format: Full content with black bands
- Best for: Strategy game content

## Installation

No additional installation required! The 4X version uses the same dependencies as the original:

1. Make sure you have the original shorts creator working
2. Place both new files in your Project GameVids directory
3. Run `createshortsfor4x.bat` instead of `createwithbeatifulcaptions.bat`

## Tips for Best Results

### Image Selection
- Use screenshots that show the full game interface
- Include strategic overview maps
- Show complex diplomatic or technology screens
- Capture moments that demonstrate strategic depth

### Script Writing
- Focus on strategic thinking and planning
- Mention specific 4X mechanics (research, diplomacy, expansion)
- Emphasize long-term consequences and empire building
- Use vocabulary that appeals to strategy game fans

### Video Processing
- The black bands are intentional - they preserve important information
- Longer image duration works well for strategy games (viewers need time to absorb complex information)
- Consider starting videos at strategic decision points rather than action sequences

## Troubleshooting

### Video Looks "Small" with Black Bars
This is **intentional and correct** for 4X games. The black bands preserve all strategic information that would otherwise be lost to cropping.

### UI Elements Not Visible
If UI elements are still not visible, try:
1. Using higher resolution source images
2. Adjusting the video start time to show clearer strategic moments
3. Selecting screenshots with less UI clutter

### Performance
The 4X version may process slightly slower due to the additional image processing steps, but the quality improvement for strategy games is significant.

## Recent Fixes

### TTS Audio Generation Fixed (v1.1)
- **Issue**: TTS was failing with `module 'chatterbox' has no attribute 'TTS'`
- **Fix**: Updated to use correct ChatterboxTTS API matching the working original
- **Improvement**: Added 4X-specific TTS settings for better strategy game narration

### Path Object Handling Fixed (v1.2)
- **Issue**: Video creation failing with `'WindowsPath' object has no attribute 'endswith'`
- **Fix**: Convert Path objects to strings when passing to MoviePy and torchaudio functions
- **Locations Fixed**: TTS audio loading, video creation, and caption generation

---

**Remember**: The goal of the 4X version is information preservation over visual drama. Every strategic element matters in 4X games! 