"""
Asset management for downloading and processing game assets
"""

import logging
import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

from .config import config
from .utils import (
    create_safe_name, 
    extract_steam_app_id, 
    download_file,
    is_valid_image_file,
    is_valid_video_file
)

logger = logging.getLogger(__name__)

class AssetManager:
    """Manages downloading and organizing game assets"""
    
    def __init__(self):
        self.assets_dir = config.get_directory("assets")
        self.temp_dir = config.get_directory("temp")
        
    def download_game_assets(self, game_name: str, steam_url: Optional[str] = None) -> Tuple[str, Dict]:
        """
        Download game assets from Steam and other sources
        
        Returns:
            Tuple of (assets_directory_path, metadata_dict)
        """
        safe_name = create_safe_name(game_name)
        game_assets_dir = self.assets_dir / safe_name
        images_dir = game_assets_dir / "images"
        videos_dir = game_assets_dir / "videos"
        
        # Create directories
        for directory in [game_assets_dir, images_dir, videos_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Check if we already have sufficient assets
        existing_images = len(list(images_dir.glob('*.jpg')))
        if existing_images >= config.get("assets.max_images", 10):
            logger.info(f"[FOUND] {existing_images} existing images for {game_name}")
            return str(game_assets_dir), self._load_metadata(game_assets_dir)
        
        # Initialize metadata
        metadata = {
            "game_name": game_name,
            "safe_name": safe_name,
            "download_date": datetime.now().isoformat(),
            "steam_url": steam_url,
            "images_downloaded": 0,
            "videos_downloaded": 0
        }
        
        # Download from Steam if URL provided
        if steam_url:
            steam_metadata = self._download_steam_assets(steam_url, images_dir, videos_dir)
            metadata.update(steam_metadata)
        
        # Create placeholder assets if we don't have enough
        if metadata["images_downloaded"] < 5:
            placeholder_count = self._create_placeholder_assets(game_name, images_dir)
            metadata["images_downloaded"] += placeholder_count
            metadata["placeholder_assets"] = True
        
        # Save metadata
        self._save_metadata(game_assets_dir, metadata)
        
        logger.info(f"[READY] Assets ready: {metadata['images_downloaded']} images, "
                   f"{metadata['videos_downloaded']} videos")
        
        return str(game_assets_dir), metadata
    
    def _download_steam_assets(self, steam_url: str, images_dir: Path, videos_dir: Path) -> Dict:
        """Download assets from Steam API"""
        metadata = {"images_downloaded": 0, "videos_downloaded": 0}
        
        try:
            app_id = extract_steam_app_id(steam_url)
            if not app_id:
                logger.error("Could not extract Steam App ID from URL")
                return metadata
            
            # Get data from Steam API
            api_url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            
            response = requests.get(api_url, headers=headers, timeout=30)
            data = response.json()
            
            if not data or not data.get(app_id, {}).get('success', False):
                logger.warning("Steam API request failed")
                return metadata
            
            app_data = data[app_id]['data']
            
            # Update metadata with Steam info
            metadata.update({
                "app_id": app_id,
                "name": app_data.get('name', ''),
                "description": app_data.get('short_description', ''),
                "detailed_description": app_data.get('detailed_description', ''),
                "genres": [genre['description'] for genre in app_data.get('genres', [])],
                "developers": app_data.get('developers', []),
                "publishers": app_data.get('publishers', []),
                "release_date": app_data.get('release_date', {}).get('date', ''),
            })
            
            # Download screenshots
            screenshots = app_data.get('screenshots', [])
            max_images = config.get("assets.max_images", 15)
            
            for i, screenshot in enumerate(screenshots[:max_images]):
                img_url = screenshot.get('path_full')
                if img_url:
                    img_path = images_dir / f"screenshot_{i+1:02d}.jpg"
                    if download_file(img_url, img_path):
                        metadata["images_downloaded"] += 1
                    time.sleep(0.5)  # Rate limiting
            
            # Download trailer if available
            movies = app_data.get('movies', [])
            if movies:
                movie_url = movies[0].get('mp4', {}).get('max')
                if movie_url:
                    video_path = videos_dir / f"{create_safe_name(metadata.get('name', 'game'))}_trailer.mp4"
                    if download_file(movie_url, video_path):
                        metadata["videos_downloaded"] += 1
            
            logger.info(f"[DOWNLOADED] {metadata['images_downloaded']} images from Steam")
            
        except Exception as e:
            logger.error(f"[ERROR] Steam asset download failed: {e}")
        
        return metadata
    
    def _create_placeholder_assets(self, game_name: str, images_dir: Path, count: int = 5) -> int:
        """Create placeholder images when real assets aren't available"""
        try:
            colors = [
                (70, 130, 180),   # Steel blue
                (255, 160, 122),  # Light salmon
                (152, 251, 152),  # Pale green
                (255, 69, 0),     # Red orange
                (147, 112, 219),  # Medium purple
            ]
            
            for i in range(count):
                img = Image.new('RGB', (1920, 1080), colors[i % len(colors)])
                draw = ImageDraw.Draw(img)
                
                # Try to use custom font
                try:
                    font_path = config.get_directory("fonts") / "Roboto-Bold.ttf"
                    if font_path.exists():
                        font = ImageFont.truetype(str(font_path), 120)
                    else:
                        font = ImageFont.truetype("arial.ttf", 120)
                except:
                    font = ImageFont.load_default()
                
                # Add text
                text = f"{game_name}\nPlaceholder Image {i+1}"
                
                # Calculate text position (center)
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                x = (1920 - text_width) // 2
                y = (1080 - text_height) // 2
                
                # Draw text with outline
                outline_color = (0, 0, 0)
                text_color = (255, 255, 255)
                
                # Draw outline
                for dx in [-2, -1, 0, 1, 2]:
                    for dy in [-2, -1, 0, 1, 2]:
                        if dx != 0 or dy != 0:
                            draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
                
                # Draw main text
                draw.text((x, y), text, font=font, fill=text_color)
                
                # Save image
                img_path = images_dir / f"placeholder_{i+1:02d}.jpg"
                img.save(img_path, 'JPEG', quality=90)
            
            logger.info(f"[CREATED] {count} placeholder images for {game_name}")
            return count
            
        except Exception as e:
            logger.error(f"[ERROR] Placeholder creation failed: {e}")
            return 0
    
    def _save_metadata(self, assets_dir: Path, metadata: Dict):
        """Save asset metadata to JSON file"""
        try:
            metadata_file = assets_dir / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
    
    def _load_metadata(self, assets_dir: Path) -> Dict:
        """Load asset metadata from JSON file"""
        try:
            metadata_file = assets_dir / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")
        
        return {}
    
    def get_image_files(self, assets_dir: str, max_count: Optional[int] = None) -> List[str]:
        """Get list of valid image files from assets directory"""
        images_dir = Path(assets_dir) / "images"
        if not images_dir.exists():
            return []
        
        # Get all valid image files
        image_files = []
        for pattern in config.get("assets.image_formats", ["jpg", "jpeg", "png"]):
            for img_file in images_dir.glob(f'*.{pattern}'):
                if is_valid_image_file(img_file, config.get("assets.min_file_size", 30000)):
                    image_files.append(str(img_file))
        
        # Sort by file size (bigger = better quality)
        image_files.sort(key=lambda x: Path(x).stat().st_size, reverse=True)
        
        # Limit count if specified
        if max_count:
            image_files = image_files[:max_count]
        
        logger.info(f"[IMAGES] Found {len(image_files)} valid images")
        return image_files
    
    def get_video_files(self, assets_dir: str) -> List[str]:
        """Get list of valid video files from assets directory"""
        videos_dir = Path(assets_dir) / "videos"
        if not videos_dir.exists():
            return []
        
        video_files = []
        for pattern in config.get("assets.video_formats", ["mp4", "avi", "mov"]):
            for video_file in videos_dir.glob(f'*.{pattern}'):
                if is_valid_video_file(video_file):
                    video_files.append(str(video_file))
        
        logger.info(f"[VIDEOS] Found {len(video_files)} valid videos")
        return video_files