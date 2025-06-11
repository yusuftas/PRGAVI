"""
Shared utility functions for PRGAVI
"""

import os
import re
import logging
from pathlib import Path
from typing import Optional, List
from datetime import datetime
import requests

logger = logging.getLogger(__name__)

def create_safe_name(name: str) -> str:
    """Create a safe filename from game name by removing illegal characters"""
    # Remove illegal characters and replace with underscores
    safe = re.sub(r'[<>:"/\\|?*]', '_', name)
    # Replace spaces and dashes with underscores
    safe = safe.replace(' ', '_').replace('-', '_')
    # Remove multiple consecutive underscores
    safe = re.sub(r'_+', '_', safe)
    # Convert to lowercase and strip underscores from ends
    return safe.lower().strip('_')

def ensure_directories(directories: List[str]) -> bool:
    """Ensure multiple directories exist"""
    try:
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            
            # Create .gitkeep file if it doesn't exist
            gitkeep = Path(directory) / ".gitkeep"
            if not gitkeep.exists():
                gitkeep.write_text("# This directory is part of the project structure\n")
        
        logger.info(f"[DIRS] Created/verified {len(directories)} directories")
        return True
    except Exception as e:
        logger.error(f"[ERROR] Failed to create directories: {e}")
        return False

def get_project_root() -> Path:
    """Get the project root directory"""
    return Path(__file__).parent.parent

def validate_steam_url(url: str) -> bool:
    """Validate if a URL is a valid Steam store URL"""
    if not url:
        return False
    
    steam_patterns = [
        r'https?://store\.steampowered\.com/app/\d+/',
        r'https?://steamcommunity\.com/app/\d+',
        r'steampowered\.com/app/\d+'
    ]
    
    return any(re.search(pattern, url) for pattern in steam_patterns)

def extract_steam_app_id(url: str) -> Optional[str]:
    """Extract Steam App ID from URL"""
    if not url:
        return None
        
    match = re.search(r'/app/(\d+)/', url)
    return match.group(1) if match else None

def extract_game_name_from_url(steam_url: str) -> str:
    """Extract game name from Steam URL"""
    try:
        # Try to extract from URL path
        match = re.search(r'/app/\d+/([^/?]+)', steam_url)
        if match:
            game_name = match.group(1).replace('_', ' ').replace('-', ' ')
            # Clean up and capitalize
            game_name = ' '.join(word.capitalize() for word in game_name.split())
            return game_name
    except Exception:
        pass
    return "Unknown Game"

def download_file(url: str, destination: Path, timeout: int = 30) -> bool:
    """Download a file from URL to destination"""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, stream=True, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # Ensure destination directory exists
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(destination, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        progress = downloaded / total_size * 100
                        print(f"\rDownloading {destination.name}: {progress:.1f}%", end='', flush=True)
        
        if total_size > 0:
            print()  # New line after progress
            
        logger.info(f"[DOWNLOAD] Downloaded: {destination}")
        return True
        
    except Exception as e:
        logger.error(f"[ERROR] Download failed {destination}: {e}")
        return False

def get_file_size_mb(file_path: Path) -> float:
    """Get file size in megabytes"""
    if file_path.exists():
        return file_path.stat().st_size / (1024 * 1024)
    return 0.0

def cleanup_files(file_paths: List[Path], ignore_errors: bool = True):
    """Clean up multiple files"""
    for file_path in file_paths:
        try:
            if file_path.exists():
                file_path.unlink()
                logger.debug(f"Cleaned up: {file_path}")
        except Exception as e:
            if not ignore_errors:
                raise
            logger.warning(f"Failed to cleanup {file_path}: {e}")

def estimate_duration(text: str, words_per_minute: int = 180) -> float:
    """Estimate speech duration in seconds"""
    word_count = len(text.split())
    duration_minutes = word_count / words_per_minute
    return duration_minutes * 60

def truncate_text_by_words(text: str, max_words: int) -> str:
    """Truncate text to maximum word count"""
    words = text.split()
    if len(words) <= max_words:
        return text
    
    truncated = ' '.join(words[:max_words])
    
    # Try to end on a complete sentence
    sentences = truncated.split('.')
    if len(sentences) > 1:
        return '. '.join(sentences[:-1]) + '.'
    
    return truncated

def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """Setup logging configuration"""
    handlers = [logging.StreamHandler()]
    
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_path))
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=handlers
    )
    
    return logging.getLogger("PRGAVI")

def format_timestamp() -> str:
    """Get current timestamp as string"""
    return datetime.now().strftime('%Y%m%d_%H%M%S')

def is_valid_image_file(file_path: Path, min_size: int = 30000) -> bool:
    """Check if file is a valid image with minimum size"""
    if not file_path.exists():
        return False
        
    # Check file size
    if file_path.stat().st_size < min_size:
        return False
        
    # Check file extension
    valid_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    return file_path.suffix.lower() in valid_extensions

def is_valid_video_file(file_path: Path) -> bool:
    """Check if file is a valid video"""
    if not file_path.exists():
        return False
        
    valid_extensions = {'.mp4', '.avi', '.mov', '.mkv'}
    return file_path.suffix.lower() in valid_extensions