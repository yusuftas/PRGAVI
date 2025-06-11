# Changelog

All notable changes to PRGAVI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-06-11

### 🚀 Major Refactoring - Modular Architecture

#### Added
- ✨ **Modern GUI Interface** (`prgavi_gui.py`) with dark theme
- 💻 **Unified CLI Interface** (`prgavi_unified.py`) with all modes
- 📁 **Modular `lib/` System** - Reusable, maintainable code
- 🎮 **Three Creation Modes**: Standard, 4X Strategy, Beautiful Captions
- ⚙️ **Centralized Configuration** with JSON file support
- 📊 **Enhanced Logging** and progress tracking
- 🔧 **Flexible Video Processing** with mode-specific layouts

#### Removed  
- 🗑️ **9 Obsolete Python Scripts** (consolidated functionality)
- 🗑️ **5 Legacy Batch Files** (replaced by modern interfaces)
- 🗑️ **Old `core/` Architecture** (GameVids automation system)
- 🗑️ **Unused `tools/` Folder** (ImageMagick configs)

#### Changed
- 🔄 **Complete Code Consolidation** - No more duplication
- 🏗️ **New Architecture**: `lib/` modules + unified entry points
- 📁 **Games Folder**: Now local-only (excluded from Git)
- 🖥️ **GUI Redesign**: Modern interface with real-time progress
- 📖 **Updated Documentation** reflecting new usage patterns

#### Modules Created
- `lib/config.py` - Configuration management
- `lib/assets.py` - Asset downloading & management  
- `lib/video.py` - Video processing with multiple modes
- `lib/captions.py` - Caption generation (standard + beautiful)
- `lib/tts.py` - Text-to-speech processing
- `lib/catalog.py` - Game catalog management
- `lib/utils.py` - Shared utilities

#### Migration Guide
- **Old**: `shortscreator.py` → **New**: `python prgavi_unified.py --mode standard`
- **Old**: `shortscreatorfor4x.py` → **New**: `python prgavi_unified.py --mode 4x`  
- **Old**: `shortscreatorwithbeautifulcaptions.py` → **New**: `python prgavi_unified.py --mode beautiful_captions`
- **Old**: Various GUIs → **New**: `python prgavi_gui.py`

## [1.0.0] - 2025-06-04

### Added
- ✨ **Complete automation** with Steam URL processing
- 🎬 **Professional video creation** with MoviePy 1.0.3
- 🔊 **AI-powered narration** using Chatterbox TTS
- 📝 **Beautiful captions** with Captacity integration
- 📁 **Organized project structure** with game-specific folders
- 🚀 **Batch file launcher** for easy one-click operation
- 📊 **Comprehensive catalog system** for tracking progress
- 🎯 **Mobile-optimized output** (1080x1920 resolution)
- 🔄 **Robust error handling** with UTF-8 encoding fixes
- 📖 **Extensive documentation** with usage guides

### Features
- **Steam Integration**: Automatic asset downloading from Steam URLs
- **Smart Asset Management**: High-quality screenshots and trailers
- **Dynamic Video Layout**: Image slideshow + gameplay footage
- **Word-by-word Captions**: Gold highlighting with beautiful styling
- **Interactive Script Input**: Custom scripts or auto-generation
- **Video Start Time Control**: Start gameplay at specific seconds
- **Fallback Systems**: Placeholder assets when downloads fail
- **Batch Processing**: Multiple games with organized catalogs

### Technical
- **Python 3.8+** compatibility
- **Windows 10/11** optimized
- **Virtual environment** support
- **Automated dependency installation**
- **GitHub Actions** CI/CD pipeline
- **MIT License** for open source use

### Documentation
- 📖 Comprehensive README with examples
- 🚀 Quick start guides
- 🛠️ Troubleshooting section
- 🤝 Contributing guidelines
- 📊 Performance metrics
- 🎯 Script writing guidelines

---

## Future Releases

### [1.1.0] - Planned
- 🎨 Custom video themes and templates
- 🌐 Epic Games and GOG platform support
- 📱 Better mobile caption positioning
- 🎵 Background music integration
- 🔧 Advanced configuration options

### [1.2.0] - Planned
- 🤖 AI-powered script generation improvements
- ☁️ Cloud processing options
- 📊 Advanced analytics and metrics
- 🎬 Professional editing features
- 📱 Mobile companion app

---

**Legend:**
- ✨ New Features
- 🎬 Video Processing
- 🔊 Audio Features
- 📝 Caption Features
- 🛠️ Technical Improvements
- 📖 Documentation
- 🐛 Bug Fixes
- 🔧 Configuration
- 📊 Analytics 