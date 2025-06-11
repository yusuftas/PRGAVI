"""
Game catalog management for tracking processed games
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from .config import config
from .utils import create_safe_name

logger = logging.getLogger(__name__)

class CatalogManager:
    """Manages game catalog for tracking processing history"""
    
    def __init__(self, catalog_type: str = "standard"):
        self.catalog_dir = config.get_directory("catalog")
        self.catalog_type = catalog_type
        
        # Set catalog file based on type
        if catalog_type == "4x":
            self.catalog_file = self.catalog_dir / "game_catalog_4x.json"
        else:
            self.catalog_file = self.catalog_dir / "game_catalog.json"
        
        self.catalog_dir.mkdir(parents=True, exist_ok=True)
    
    def update_game_entry(self, game_name: str, steam_url: Optional[str] = None, 
                         status: str = "started", **kwargs) -> Dict:
        """
        Update or create game catalog entry
        
        Args:
            game_name: Name of the game
            steam_url: Steam URL (optional)
            status: Current processing status
            **kwargs: Additional metadata
            
        Returns:
            Updated game entry dictionary
        """
        # Load existing catalog
        catalog = self._load_catalog()
        
        # Find or create game entry
        game_entry = self._find_game_entry(catalog, game_name)
        
        if not game_entry:
            # Create new entry
            game_entry = {
                "name": game_name,
                "safe_name": create_safe_name(game_name),
                "steam_url": steam_url,
                "created_date": datetime.now().isoformat(),
                "status": status,
                "assets_downloaded": False,
                "video_created": False,
                "processing_history": [],
                "catalog_type": self.catalog_type
            }
            
            # Add 4X-specific fields
            if self.catalog_type == "4x":
                game_entry["video_type"] = "4X_no_zoom"
            
            catalog["games"].append(game_entry)
            catalog["stats"]["total_games"] += 1
        
        # Update entry
        game_entry["status"] = status
        game_entry["last_updated"] = datetime.now().isoformat()
        
        # Add any additional metadata
        for key, value in kwargs.items():
            game_entry[key] = value
        
        # Update processing history
        game_entry["processing_history"].append({
            "timestamp": datetime.now().isoformat(),
            "status": status,
            **kwargs
        })
        
        # Update status counts
        if status == "completed":
            game_entry["video_created"] = True
            catalog["stats"]["completed"] += 1
        elif status == "assets_downloaded":
            game_entry["assets_downloaded"] = True
        
        # Save catalog
        self._save_catalog(catalog)
        
        logger.info(f"[CATALOG] Updated: {game_name} - {status}")
        return game_entry
    
    def get_game_entry(self, game_name: str) -> Optional[Dict]:
        """Get game entry from catalog"""
        catalog = self._load_catalog()
        return self._find_game_entry(catalog, game_name)
    
    def list_games(self, status_filter: Optional[str] = None) -> List[Dict]:
        """
        List games from catalog
        
        Args:
            status_filter: Filter by status (optional)
            
        Returns:
            List of game entries
        """
        catalog = self._load_catalog()
        games = catalog.get("games", [])
        
        if status_filter:
            games = [game for game in games if game.get("status") == status_filter]
        
        return games
    
    def get_catalog_stats(self) -> Dict:
        """Get catalog statistics"""
        catalog = self._load_catalog()
        return catalog.get("stats", {"total_games": 0, "completed": 0})
    
    def show_catalog_summary(self) -> str:
        """Generate human-readable catalog summary"""
        if not self.catalog_file.exists():
            return f"[CATALOG] No {self.catalog_type} games in catalog yet"
        
        catalog = self._load_catalog()
        stats = catalog.get("stats", {})
        games = catalog.get("games", [])
        
        summary_lines = []
        summary_lines.append(f"[CATALOG] {self.catalog_type.upper()} GAME CATALOG")
        summary_lines.append("=" * 50)
        summary_lines.append(f"Total Games: {stats.get('total_games', 0)}")
        summary_lines.append(f"Completed: {stats.get('completed', 0)}")
        
        if stats.get('total_games', 0) > 0:
            success_rate = (stats.get('completed', 0) / stats['total_games']) * 100
            summary_lines.append(f"Success Rate: {success_rate:.1f}%")
        
        summary_lines.append("")
        summary_lines.append("[GAMES]")
        
        for game in games:
            status_icon = self._get_status_icon(game.get("status", "unknown"))
            game_line = f"   {status_icon} {game['name']}"
            
            # Add creation date
            created_date = game.get('created_date', '')[:10] if game.get('created_date') else 'Unknown'
            game_line += f" ({created_date})"
            
            # Add video type for 4X
            if self.catalog_type == "4x" and game.get("video_type"):
                game_line += f" - {game['video_type']}"
            
            summary_lines.append(game_line)
        
        return "\n".join(summary_lines)
    
    def export_catalog(self, export_path: Optional[str] = None) -> str:
        """Export catalog to JSON file"""
        if not export_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_path = self.catalog_dir / f"catalog_export_{self.catalog_type}_{timestamp}.json"
        
        catalog = self._load_catalog()
        
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(catalog, f, indent=2, ensure_ascii=False)
            
            logger.info(f"[EXPORT] Catalog exported to: {export_path}")
            return str(export_path)
        except Exception as e:
            logger.error(f"Failed to export catalog: {e}")
            raise
    
    def _load_catalog(self) -> Dict:
        """Load catalog from file or create default"""
        if self.catalog_file.exists():
            try:
                with open(self.catalog_file, 'r', encoding='utf-8', errors='replace') as f:
                    catalog = json.load(f)
                
                # Ensure required structure
                if "games" not in catalog:
                    catalog["games"] = []
                if "stats" not in catalog:
                    catalog["stats"] = {"total_games": 0, "completed": 0}
                
                return catalog
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.warning(f"Error reading catalog: {e}, creating new one")
        
        # Create default catalog
        default_catalog = {
            "games": [],
            "stats": {"total_games": 0, "completed": 0},
            "catalog_type": self.catalog_type,
            "created_date": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        if self.catalog_type == "4x":
            default_catalog["description"] = "Catalog for 4X strategy games with specialized video processing"
        
        return default_catalog
    
    def _save_catalog(self, catalog: Dict):
        """Save catalog to file"""
        try:
            catalog["last_updated"] = datetime.now().isoformat()
            
            with open(self.catalog_file, 'w', encoding='utf-8') as f:
                json.dump(catalog, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save catalog: {e}")
            raise
    
    def _find_game_entry(self, catalog: Dict, game_name: str) -> Optional[Dict]:
        """Find game entry in catalog by name"""
        for game in catalog.get("games", []):
            if game.get("name") == game_name:
                return game
        return None
    
    def _get_status_icon(self, status: str) -> str:
        """Get status icon for status"""
        status_icons = {
            "completed": "[DONE]",
            "started": "[ACTIVE]",
            "processing": "[WORKING]",
            "assets_downloaded": "[ASSETS]",
            "assets_ready": "[READY]",
            "failed": "[ERROR]",
            "cancelled": "[CANCEL]"
        }
        return status_icons.get(status, "[UNKNOWN]")