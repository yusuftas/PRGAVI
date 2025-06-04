# Contributing to PRGAVI

Thank you for your interest in contributing to PRGAVI! 🎉

## 🚀 Getting Started

### Development Setup
1. **Fork** the repository
2. **Clone** your fork locally
3. **Create** a virtual environment
4. **Install** dependencies

```bash
git clone https://github.com/yourusername/PRGAVI.git
cd PRGAVI
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Development Dependencies
```bash
pip install pytest black flake8
```

## 🔧 Development Guidelines

### Code Style
- **Python**: Follow PEP 8 standards
- **Formatting**: Use `black` for code formatting
- **Linting**: Use `flake8` for code quality
- **Comments**: Write clear, descriptive comments

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black shortscreator.py
flake8 shortscreator.py
```

## 📝 Contribution Types

### 🐛 Bug Reports
When reporting bugs, please include:
- **OS version** (Windows 10/11)
- **Python version** (3.8+)
- **Error messages** (full traceback)
- **Steps to reproduce**
- **Steam URL** that caused the issue

### ✨ Feature Requests
For new features, please provide:
- **Clear description** of the feature
- **Use case** and benefits
- **Implementation suggestions** (if any)
- **Mockups** or examples (if applicable)

### 🔧 Code Contributions
1. **Create** a feature branch
2. **Make** your changes
3. **Test** thoroughly
4. **Format** your code
5. **Submit** a pull request

```bash
git checkout -b feature/amazing-new-feature
# Make your changes
git add .
git commit -m "Add amazing new feature"
git push origin feature/amazing-new-feature
```

## 🎯 Areas for Contribution

### High Priority
- 🐛 **Bug fixes** - Especially encoding and compatibility issues
- 📱 **Mobile optimization** - Better caption positioning and sizing
- 🎨 **UI improvements** - Better user experience and error messages
- 📊 **Performance** - Faster processing and rendering

### Medium Priority
- 🌐 **Platform support** - Epic Games, GOG integration
- 🎵 **Audio enhancements** - Music and sound effects
- 🎨 **Visual themes** - Customizable video templates
- 📈 **Analytics** - Better progress tracking and metrics

### Low Priority
- 🤖 **AI improvements** - Better script generation
- ☁️ **Cloud features** - Remote processing options
- 📱 **Mobile app** - Companion mobile application
- 🔧 **Advanced features** - Professional editing tools

## 🛡️ Quality Standards

### Code Requirements
- ✅ **Functionality**: New code must work as intended
- ✅ **Testing**: Include tests for new features
- ✅ **Documentation**: Update relevant documentation
- ✅ **Compatibility**: Maintain Windows 10/11 compatibility
- ✅ **Performance**: Don't significantly slow down processing

### Pull Request Guidelines
1. **Descriptive title** summarizing the change
2. **Detailed description** of what and why
3. **Testing notes** - how you tested the changes
4. **Breaking changes** - highlight any compatibility issues
5. **Screenshots** or videos for UI changes

## 🔍 Review Process

### What We Look For
- **Code quality** - Clean, readable, maintainable
- **Performance** - No significant slowdowns
- **Compatibility** - Works on target platforms
- **Documentation** - Updated README, comments, etc.
- **Testing** - Adequate test coverage

### Review Timeline
- **Initial review**: Within 48 hours
- **Follow-up**: Within 24 hours
- **Merge**: Once approved by maintainers

## 🎮 Testing Guidelines

### Manual Testing
1. **Install** fresh environment
2. **Test** basic functionality with multiple games
3. **Verify** batch file operation
4. **Check** output quality
5. **Test** error conditions

### Automated Testing
```bash
pytest tests/ -v
```

### Test Data
Use these Steam URLs for testing:
- `https://store.steampowered.com/app/2622380/ELDEN_RING_NIGHTREIGN/`
- `https://store.steampowered.com/app/275850/No_Mans_Sky/`
- `https://store.steampowered.com/app/526870/Satisfactory/`

## 📜 Code of Conduct

### Our Standards
- **Be respectful** and inclusive
- **Use welcoming** and inclusive language
- **Accept constructive criticism** gracefully
- **Focus on community benefit** over personal gain
- **Show empathy** towards community members

### Unacceptable Behavior
- Harassment or discriminatory language
- Trolling or inflammatory comments
- Personal attacks or insults
- Spam or off-topic content

## 🎯 Getting Help

### Documentation
- 📖 [README.md](README.md) - Main documentation
- 📝 [BATCH_USAGE_README.md](BATCH_USAGE_README.md) - Usage guide
- 🔧 Code comments and docstrings

### Community
- 💬 **GitHub Discussions** - For questions and ideas
- 🐛 **GitHub Issues** - For bugs and feature requests
- 📧 **Email** - For private matters

### Development Help
- 🤝 **Pair programming** - Available for complex features
- 📚 **Architecture guidance** - Help understanding codebase
- 🔧 **Setup assistance** - Help with development environment

## 🏆 Recognition

### Contributors
All contributors will be:
- 📝 **Listed** in README.md
- 🎉 **Mentioned** in release notes
- 💖 **Appreciated** by the community

### Significant Contributions
Major contributors may receive:
- 🏅 **Maintainer status**
- 🎯 **Decision-making input**
- 📢 **Public recognition**

---

**Thank you for helping make PRGAVI better!** 🚀

Your contributions help creators worldwide turn gaming content into engaging shorts. Every bug fix, feature, and improvement makes a difference in the creator community. 