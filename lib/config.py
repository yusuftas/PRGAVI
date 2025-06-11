"""
Centralized configuration management for PRGAVI
"""

import os
from pathlib import Path
from typing import Dict, Any
import json

class Config:
    """Centralized configuration manager"""
    
    def __init__(self, config_file: str = None):
        self.project_root = Path(__file__).parent.parent
        self.config_file = config_file or self.project_root / "config.json"
        self._config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            # Directories
            "directories": {
                "assets": "assets",
                "output": "output", 
                "temp": "temp",
                "games": "games",
                "catalog": "catalog",
                "fonts": "fonts"
            },
            
            # Video settings
            "video": {
                "width": 1080,
                "height": 1920,
                "fps": 30,
                "codec": "libx264",
                "audio_codec": "aac",
                "preset": "faster",
                "quality": 23
            },
            
            # TTS settings
            "tts": {
                "model": "chatterbox",
                "exaggeration": 0.3,
                "cfg_weight": 0.5,
                "temperature": 0.85,
                "words_per_minute": 180
            },
            
            # Caption settings
            "captions": {
                "font_size": 80,
                "font_color": "#FFFFFF",
                "highlight_color": "#FFD700",
                "stroke_color": "#000000",
                "stroke_width": 3,
                "shadow_strength": 2.0,
                "line_count": 1,
                "padding": 60
            },
            
            # Asset settings
            "assets": {
                "max_images": 15,
                "min_file_size": 30000,
                "image_formats": ["jpg", "jpeg", "png", "webp"],
                "video_formats": ["mp4", "avi", "mov"]
            },
            
            # Script settings
            "script": {
                "max_words": 100,
                "target_duration": 35,
                "auto_generate": True
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                # Merge with defaults
                return self._merge_configs(default_config, file_config)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
                
        return default_config
    
    def _merge_configs(self, default: Dict, custom: Dict) -> Dict:
        """Recursively merge configuration dictionaries"""
        result = default.copy()
        for key, value in custom.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def get(self, key_path: str, default=None):
        """Get configuration value using dot notation (e.g., 'video.width')"""
        keys = key_path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
                
        return value
    
    def set(self, key_path: str, value):
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self._config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
            
        config[keys[-1]] = value
    
    def save(self):
        """Save current configuration to file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config file: {e}")
    
    def get_directory(self, name: str) -> Path:
        """Get absolute path for a named directory"""
        rel_path = self.get(f"directories.{name}", name)
        return self.project_root / rel_path
    
    def ensure_directories(self):
        """Create all configured directories"""
        for dir_name in self.get("directories", {}).keys():
            dir_path = self.get_directory(dir_name)
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Create .gitkeep file
            gitkeep = dir_path / ".gitkeep"
            if not gitkeep.exists():
                gitkeep.write_text("# This directory is part of the project structure\n")

# Global config instance
config = Config()