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
- 🖱️ **Modern GUI Interface**: User-friendly graphical interface
- 💻 **Unified CLI**: Powerful command-line tool
- 📊 **Progress Tracking**: Complete catalog system
- 🔄 **Error Handling**: Robust fallback systems

## 📦 Installation

### Prerequisites
- **Windows 10/11** (primary support)
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

### Method 1: GUI Interface (Recommended)
```bash
python prgavi_gui.py
```
**Features:**
- Modern dark theme interface
- Real-time progress tracking
- Interactive script input
- Mode selection (Standard, 4X Strategy, Beautiful Captions)
- Integrated catalog viewer

### Method 2: Command Line Interface
```bash
# Interactive mode with script input
python prgavi_unified.py --game "Elden Ring Nightreign" --steam-url "https://store.steampowered.com/app/2622380/ELDEN_RING_NIGHTREIGN/"

# Beautiful captions mode
python prgavi_unified.py --game "Game Name" --mode beautiful_captions

# 4X strategy games mode (with black bands, no cropping)
python prgavi_unified.py --game "Civilization VI" --mode 4x

# Skip interactive script input
python prgavi_unified.py --game "Game Name" --no-input

# Custom video start time
python prgavi_unified.py --game "Game Name" --video-start-time 15

# Load script from file
python prgavi_unified.py --game "Game Name" --script-file "my_script.txt"

# View catalog
python prgavi_unified.py --catalog --mode standard
```

## 🎮 Creation Modes

### Standard Mode
- **Best for**: Action, adventure, RPG games
- **Layout**: 60% images (top) + 40% video (bottom)
- **Cropping**: Smart cropping for optimal viewing
- **Use case**: Most gaming content

### Beautiful Captions Mode
- **Best for**: Content requiring high-quality captions
- **Features**: Word-by-word highlighting with Captacity
- **Layout**: Same as standard + enhanced captions
- **Use case**: Professional content, accessibility

### 4X Strategy Mode
- **Best for**: Strategy games (Civilization, Total War, etc.)
- **Layout**: Black bands preserve aspect ratio
- **Cropping**: No cropping - full image preservation
- **Use case**: Complex UI games, detailed screenshots

## 📂 Project Structure

```
PRGAVI/
├── 📁 lib/                        # Modular system core
│   ├── config.py                  # Configuration management
│   ├── assets.py                  # Asset downloading & management
│   ├── video.py                   # Video processing
│   ├── captions.py                # Caption generation
│   ├── tts.py                     # Text-to-speech
│   ├── catalog.py                 # Game catalog management
│   └── utils.py                   # Shared utilities
├── 📁 games/                      # User scripts (local only)
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
├── 🖥️ prgavi_gui.py             # Modern GUI interface
├── 💻 prgavi_unified.py          # Unified CLI interface
├── 📋 requirements.txt           # Dependencies
└── 📖 Documentation files
```

## 🎯 Usage Examples

### GUI Examples
1. **Launch GUI**: `python prgavi_gui.py`
2. **Enter Steam URL**: Paste game URL or enter game name
3. **Select Mode**: Choose creation mode from radio buttons
4. **Write Script**: Enter custom script or use auto-generation
5. **Create Video**: Click "Create Video" and monitor progress

### CLI Examples

#### Example 1: Interactive Script Input
```bash
python prgavi_unified.py --game "Elden Ring Nightreign" --steam-url "https://store.steampowered.com/app/2622380/ELDEN_RING_NIGHTREIGN/"
```
**Result**: Prompts for custom script, creates professional short

#### Example 2: Beautiful Captions
```bash
python prgavi_unified.py --game "Cyberpunk 2077" --mode beautiful_captions --no-input
```
**Result**: Auto-generated script with word-by-word highlighting

#### Example 3: 4X Strategy Game
```bash
python prgavi_unified.py --game "Civilization VI" --mode 4x --video-start-time 20
```
**Result**: Strategy game video with preserved aspect ratios

#### Example 4: Batch Processing
```bash
python prgavi_unified.py --game "Satisfactory" --mode standard --no-input
python prgavi_unified.py --game "RimWorld" --mode standard --no-input
python prgavi_unified.py --game "Palworld" --mode beautiful_captions --no-input
```

## 🎬 Output Features

### Video Specifications
- **Format**: MP4 (H.264 + AAC)
- **Resolution**: 1080x1920 (Mobile optimized)
- **Duration**: 30-40 seconds
- **FPS**: 30fps
- **Audio**: High-quality AI narration

### Caption Features (Beautiful Captions Mode)
- **Word Highlighting**: Real-time word-by-word highlighting
- **Font**: Large, readable fonts optimized for mobile
- **Style**: White text with black outline and shadows
- **Colors**: Gold highlighting for current word
- **Layout**: Positioned in image section for optimal viewing

## 🛠️ Dependencies

### Core Libraries
```
moviepy==1.0.3          # Video processing
torch                   # AI models
torchaudio             # Audio processing
chatterbox-tts         # AI narration
yt-dlp                 # Media downloading
requests               # HTTP requests
Pillow                 # Image processing
beautifulsoup4         # Web scraping
numpy                  # Numerical operations
pathlib                # Path handling
```

### Optional Dependencies
```
captacity              # Enhanced captions (for beautiful captions mode)
ffmpeg                 # Video encoding (auto-detected)
```

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

## 🔧 Configuration

### Configuration File
Create `config.json` to customize settings:
```json
{
  "video": {
    "width": 1080,
    "height": 1920,
    "fps": 30,
    "quality": 23
  },
  "script": {
    "max_words": 100,
    "target_duration": 35
  },
  "captions": {
    "font_size": 80,
    "font_color": "#FFFFFF",
    "highlight_color": "#FFD700"
  }
}
```

### Command Line Options
```bash
python prgavi_unified.py [OPTIONS]

Options:
  --game TEXT              Game name (required)
  --steam-url TEXT         Steam store URL
  --script TEXT            Custom script text
  --script-file PATH       Load script from file
  --mode [standard|4x|beautiful_captions]  Creation mode
  --video-start-time INT   Video start time in seconds
  --no-input              Skip interactive script input
  --catalog               Show game catalog
  --config PATH           Custom config file
  --log-level TEXT        Logging level
  --log-file PATH         Log file path
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
- ✅ Cyberpunk 2077
- ✅ And thousands more!

## 🐛 Troubleshooting

### Common Issues

#### "Steam URL is required"
**Solution**: Ensure URL format: `https://store.steampowered.com/app/APPID/GAMENAME/`

#### "Could not extract App ID"
**Solution**: Check URL contains `/app/NUMBER/` pattern

#### GUI not launching
**Solution**: Ensure tkinter is installed: `pip install tk`

#### Beautiful captions not working
**Solution**: Install captacity dependencies or use standard mode

#### Dependencies Missing
**Solution**: Run `pip install -r requirements.txt`

### Performance Tips
- Use SSD for faster asset processing
- Close other applications during video rendering
- Use `--no-input` for batch processing
- Monitor logs with `--log-level DEBUG`

## 📈 Performance Metrics

### Typical Processing Times
- **Asset Download**: 30-60 seconds
- **TTS Generation**: 45-90 seconds
- **Video Creation**: 60-120 seconds
- **Caption Addition**: 30-60 seconds (beautiful captions mode)
- **Total**: 3-6 minutes per video

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
- 🤖 Enhanced AI-powered script generation
- 📱 Mobile app interface
- ☁️ Cloud processing option
- 🎯 Advanced targeting options

---

**Made with ❤️ for the gaming community**

*Turn any Steam game into viral shorts content!*