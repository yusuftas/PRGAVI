"""
PRGAVI Library - Reusable modules for YouTube Shorts video creation
"""

from .config import Config, config
from .utils import (
    create_safe_name,
    ensure_directories,
    get_project_root,
    validate_steam_url,
    extract_game_name_from_url,
    setup_logging
)
from .assets import AssetManager
from .video import VideoProcessor
from .captions import CaptionManager
from .tts import TTSProcessor
from .catalog import CatalogManager

__version__ = "1.0.0"
__all__ = [
    "Config",
    "config",
    "create_safe_name",
    "ensure_directories", 
    "get_project_root",
    "validate_steam_url",
    "extract_game_name_from_url",
    "setup_logging",
    "AssetManager",
    "VideoProcessor",
    "CaptionManager",
    "TTSProcessor",
    "CatalogManager"
]