# 🎮 CREATE SHORTS WITH CONTEXT - Batch File Usage

This batch file automates the entire shorts creation process with Steam URLs and optional custom scripts.

## 📋 Requirements
- Windows system with PowerShell
- Python 3.x installed
- `shortscreator.py` in the same directory
- All Python dependencies installed

## 🚀 Usage

### Basic Usage (Interactive Script)
```batch
createshortswithcontext.bat "STEAM_URL"
```

### With Custom Script
```batch
createshortswithcontext.bat "STEAM_URL" "Your custom script here"
```

## 📝 Examples

### 1. Interactive Mode (Recommended for first-time use)
```batch
createshortswithcontext.bat "https://store.steampowered.com/app/2622380/ELDEN_RING_NIGHTREIGN/"
```
- Automatically fetches game name from Steam
- Downloads assets (screenshots, trailer, metadata)
- Prompts you to enter custom script or use auto-generated
- Creates organized folders and catalog entries

### 2. With Custom Script
```batch
createshortswithcontext.bat "https://store.steampowered.com/app/275850/No_Mans_Sky/" "No Man's Sky delivers infinite exploration across 18 quintillion unique planets. Build bases, pilot starships, and discover ancient mysteries in this ever-expanding universe. Whether solo or with friends, every journey tells a different story. Available now on Steam!"
```

### 3. PowerShell Usage
```powershell
.\createshortswithcontext.bat "https://store.steampowered.com/app/APP_ID/GAME_NAME/"
```

### 4. CMD Usage
```cmd
createshortswithcontext.bat "https://store.steampowered.com/app/APP_ID/GAME_NAME/"
```

## 🔄 What the Batch File Does

1. **🔗 URL Validation**: Extracts Steam App ID from URL
2. **🎮 Game Info**: Fetches game name via Steam API
3. **📁 Organization**: Creates organized folder structure
4. **📝 Script Handling**: 
   - If script provided: Pre-saves it and runs non-interactive
   - If no script: Runs interactive mode for script input
5. **🎬 Video Creation**: Calls shortscreator.py with proper parameters
6. **📊 Catalog**: Updates game catalog with processing history
7. **✨ Post-Processing**: Offers to open output folder and play video

## 📂 Generated Structure
```
Project GameVids/
├── games/
│   └── game_name/
│       ├── script.json    # Script with metadata
│       └── script.txt     # Plain text script
├── assets/
│   └── game_name/
│       ├── images/        # Screenshots
│       ├── videos/        # Trailers
│       └── game_metadata.json
├── output/
│   └── game_name_shorts.mp4  # Final video
└── catalog/
    └── game_catalog.json     # Processing history
```

## 🎯 Features

### ✅ Automatic Steam Integration
- Extracts App ID from Steam URL
- Fetches game name via Steam API
- Downloads screenshots and trailers
- Saves complete game metadata

### ✅ Smart Script Management
- **Interactive Mode**: Prompts for custom script input
- **Pre-provided Mode**: Uses script from command line
- **Auto-generated Mode**: Creates script based on game info
- **Persistent Storage**: Saves scripts in organized folders

### ✅ Error Handling
- Validates Steam URL format
- Checks for required files
- Handles Steam API failures
- Provides helpful error messages

### ✅ User Experience
- Clear progress indicators
- Automatic virtual environment activation
- Post-completion options (open folder, play video)
- Comprehensive help messages

## 🛠️ Troubleshooting

### "Steam URL is required"
- Make sure to provide a valid Steam store URL
- Format: `https://store.steampowered.com/app/APPID/GAMENAME/`

### "Could not extract App ID"
- Check URL format is correct
- Ensure URL contains `/app/NUMBER/`

### "shortscreator.py not found"
- Run from the Project GameVids directory
- Ensure shortscreator.py exists in current folder

### "Virtual environment not found"
- Optional - script works without venv
- Create venv if you want isolated dependencies

## 📊 Script Guidelines

When providing custom scripts, follow these guidelines:

- **Length**: 80-100 words (30-35 seconds)
- **Structure**: Hook → Core Content → Call-to-Action
- **Format**: Engaging, conversational tone
- **Ending**: Question to encourage engagement

### Example Good Script:
```
"Elden Ring Nightreign brings co-op souls gameplay to perfection. Team up with friends to conquer massive bosses and explore interconnected worlds in FromSoftware's masterpiece. Every death teaches, every victory feels earned. This is the co-op adventure souls fans have dreamed of. Coming soon to Steam. What's your favorite co-op challenge?"
```

## 🎮 Supported Games

Any game on Steam with:
- Valid Steam store page
- Available screenshots
- Accessible via Steam API

Popular examples:
- Elden Ring Nightreign
- No Man's Sky
- Satisfactory
- Stellar Blade
- And thousands more!

## 🔄 Batch Processing

For multiple games, run the batch file multiple times:

```batch
createshortswithcontext.bat "https://store.steampowered.com/app/2622380/ELDEN_RING_NIGHTREIGN/"
createshortswithcontext.bat "https://store.steampowered.com/app/275850/No_Mans_Sky/"
createshortswithcontext.bat "https://store.steampowered.com/app/526870/Satisfactory/"
```

Each game will have its own organized folder structure and catalog entry.

---

🎯 **Ready to create amazing shorts?** Just copy a Steam URL and run the batch file! 