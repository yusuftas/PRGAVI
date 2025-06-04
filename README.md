# 🎮 PRGAVI - Professional Gaming Video Creator

**Professional shorts video creator with AI narration, beautiful captions, and automated Steam asset downloading**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MoviePy](https://img.shields.io/badge/MoviePy-1.0.3-orange.svg)](https://github.com/Zulko/moviepy)

## 🚀 Features

### ✨ **Complete Automation**
- 🔗 **Steam Integration**: Automatic asset downloading from Steam URLs
- 🎯 **Smart Asset Management**: High-quality screenshots and trailers
- 📁 **Organized Structure**: Game-specific folders and catalogs
- 🎬 **Professional Videos**: Mobile-optimized 1080x1920 format

### 🎨 **Beautiful Output**
- 🔊 **AI Narration**: High-quality TTS with Chatterbox
- 📝 **Stunning Captions**: Word-by-word highlighting with Captacity
- 🎞️ **Dynamic Layout**: Image slideshow + gameplay footage
- ⚡ **Fast Processing**: Optimized for batch creation

### 🛠️ **Easy to Use**
- 🖱️ **One-Click Creation**: Simple batch file execution
- 📊 **Progress Tracking**: Complete catalog system
- 🔄 **Error Handling**: Robust fallback systems
- 📖 **Comprehensive Docs**: Detailed usage guides

## 📦 Installation

### Prerequisites
- **Windows 10/11** (batch files optimized for Windows)
- **Python 3.8+** with pip
- **Git** (for cloning)

### Quick Setup
```bash
git clone https://github.com/yourusername/PRGAVI.git
cd PRGAVI
pip install -r requirements.txt
```

### Virtual Environment (Recommended)
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 🚀 Quick Start

### Method 1: Batch File (Easiest)
```batch
# Interactive mode - prompts for custom script
createshortswithcontext.bat "https://store.steampowered.com/app/2622380/ELDEN_RING_NIGHTREIGN/"

# With custom script
createshortswithcontext.bat "STEAM_URL" "Your amazing script here"
```

### Method 2: Direct Python
```bash
# Interactive mode
python shortscreator.py --game "Elden Ring Nightreign" --steam-url "https://store.steampowered.com/app/2622380/ELDEN_RING_NIGHTREIGN/"

# View catalog
python shortscreator.py --catalog
```

## 📂 Project Structure

```
PRGAVI/
├── 📁 games/                      # Game-specific scripts & configs
│   └── elden_ring_nightreign/
│       ├── script.json            # Script with metadata
│       └── script.txt             # Plain text script
├── 📁 assets/                     # Downloaded game assets
│   └── elden_ring_nightreign/
│       ├── images/                # Screenshots
│       ├── videos/                # Trailers
│       └── game_metadata.json    # Steam API data
├── 📁 output/                     # Final videos
├── 📁 catalog/                    # Processing history
├── 🎬 shortscreator.py           # Main application
├── 🚀 createshortswithcontext.bat # Batch file launcher
├── 📖 BATCH_USAGE_README.md      # Detailed usage guide
└── 📋 requirements.txt           # Dependencies
```

## 🎯 Usage Examples

### Example 1: Elden Ring Nightreign
```batch
createshortswithcontext.bat "https://store.steampowered.com/app/2622380/ELDEN_RING_NIGHTREIGN/"
```
**Result**: Professional 30-second short with AI narration about co-op souls gameplay

### Example 2: No Man's Sky
```batch
createshortswithcontext.bat "https://store.steampowered.com/app/275850/No_Mans_Sky/" "Explore infinite worlds in No Man's Sky! Build bases on alien planets, discover ancient mysteries, and pilot starships through cosmic storms. Available now on Steam!"
```
**Result**: Custom script with space exploration visuals

### Example 3: Batch Processing
```batch
createshortswithcontext.bat "https://store.steampowered.com/app/526870/Satisfactory/"
createshortswithcontext.bat "https://store.steampowered.com/app/294100/RimWorld/"
createshortswithcontext.bat "https://store.steampowered.com/app/1623730/Palworld/"
```
**Result**: Multiple games processed with organized catalogs

## 🎬 Output Features

### Video Specifications
- **Format**: MP4 (H.264 + AAC)
- **Resolution**: 1080x1920 (Mobile optimized)
- **Duration**: 30-40 seconds
- **FPS**: 30fps
- **Audio**: High-quality AI narration

### Caption Features
- **Font Size**: 130px for mobile readability
- **Style**: White text with black outline
- **Highlighting**: Gold word-by-word highlighting
- **Layout**: 2-line maximum for optimal viewing
- **Effects**: Enhanced shadows and stroke

## 🛠️ Dependencies

### Core Libraries
```
moviepy==1.0.3          # Video processing (specific version for Captacity)
captacity               # Beautiful captions
torch                   # AI models
torchaudio             # Audio processing
chatterbox-tts         # AI narration
yt-dlp                 # Media downloading
requests               # HTTP requests
Pillow                 # Image processing
beautifulsoup4         # Web scraping
```

### Auto-Installation
The application automatically installs missing dependencies on first run.

## 📊 Script Guidelines

### Perfect Script Structure
1. **Hook** (10-15 words): Grab attention immediately
2. **Core Content** (50-70 words): Key features and gameplay
3. **Call-to-Action** (10-15 words): Encourage engagement

### Example Script Template
```
[Game] delivers [unique feature] that changes everything. Experience [key gameplay elements] in ways never seen before. Whether you're [target audience A] or [target audience B], every moment brings new discoveries. Available now on Steam. What's your [relevant question]? Follow for more gaming content!
```

### Word Count Guidelines
- **Target**: 80-100 words
- **Duration**: 30-35 seconds
- **Pacing**: ~2.5 words per second

## 🔧 Advanced Configuration

### Custom Video Start Time
```bash
python shortscreator.py --game "Game Name" --video-start-time 15
```

### Skip Interactive Mode
```bash
python shortscreator.py --game "Game Name" --no-input
```

### View Processing History
```bash
python shortscreator.py --catalog
```

## 🎯 Supported Games

### Requirements
- Valid Steam store page
- Available screenshots in Steam API
- Public game information

### Popular Examples
- ✅ Elden Ring Nightreign
- ✅ No Man's Sky
- ✅ Satisfactory
- ✅ RimWorld
- ✅ Palworld
- ✅ Stellar Blade
- ✅ And thousands more!

## 🐛 Troubleshooting

### Common Issues

#### "Steam URL is required"
**Solution**: Ensure URL format: `https://store.steampowered.com/app/APPID/GAMENAME/`

#### "Could not extract App ID"
**Solution**: Check URL contains `/app/NUMBER/` pattern

#### "UTF-8 codec can't decode"
**Solution**: Fixed in latest version with enhanced encoding handling

#### Dependencies Missing
**Solution**: Run `pip install -r requirements.txt` or let auto-installer handle it

### Performance Tips
- Use SSD for faster asset processing
- Close other applications during video rendering
- Run batch processing during off-peak hours

## 📈 Performance Metrics

### Typical Processing Times
- **Asset Download**: 30-60 seconds
- **TTS Generation**: 45-90 seconds
- **Video Creation**: 60-120 seconds
- **Caption Addition**: 30-60 seconds
- **Total**: 3-5 minutes per video

### File Sizes
- **Screenshots**: 5-10MB total
- **Trailer**: 50-100MB
- **Final Video**: 2-5MB
- **Audio**: 200-500KB

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
```bash
git clone https://github.com/yourusername/PRGAVI.git
cd PRGAVI
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **MoviePy** - Video processing foundation
- **Captacity** - Beautiful caption generation
- **Chatterbox** - High-quality TTS
- **Steam API** - Game data and assets
- **FFmpeg** - Video encoding backend

## 🚀 What's Next?

### Planned Features
- 🎨 Custom themes and templates
- 🌐 Multi-platform support (Epic, GOG)
- 🤖 AI-powered script generation
- 📱 Mobile app interface
- ☁️ Cloud processing option

---

**Made with ❤️ for the gaming community**

*Turn any Steam game into viral shorts content!* 