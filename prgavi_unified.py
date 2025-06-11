#!/usr/bin/env python3
"""
PRGAVI - Unified YouTube Shorts Creator
Refactored version using reusable modules
"""

import sys
import logging
import argparse
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

# Fix Unicode encoding issues for Windows console
if sys.platform == "win32":
    import codecs
    import locale
    try:
        # Try to set UTF-8 encoding for stdout
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')
    except (AttributeError, OSError):
        # Fallback: just ignore Unicode errors
        sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout.buffer, 'replace')
        sys.stderr = codecs.getwriter(locale.getpreferredencoding())(sys.stderr.buffer, 'replace')

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent / "lib"))

from lib import (
    Config, config,
    create_safe_name, validate_steam_url, extract_game_name_from_url,
    AssetManager, VideoProcessor, CaptionManager, TTSProcessor, CatalogManager,
    setup_logging
)

logger = logging.getLogger(__name__)

class PRGAVICreator:
    """Unified shorts creator using modular architecture"""
    
    def __init__(self, mode: str = "standard"):
        """
        Initialize PRGAVI Creator
        
        Args:
            mode: Creation mode ("standard", "4x", "beautiful_captions")
        """
        self.mode = mode
        
        # Initialize modules
        self.asset_manager = AssetManager()
        self.video_processor = VideoProcessor()
        self.caption_manager = CaptionManager()
        self.tts_processor = TTSProcessor()
        
        # Initialize catalog manager based on mode
        catalog_type = "4x" if mode == "4x" else "standard"
        self.catalog_manager = CatalogManager(catalog_type)
        
        # Ensure directories exist
        config.ensure_directories()
        
        logger.info(f"[PRGAVI] Creator initialized in {mode} mode")
    
    def create_shorts(self, game_name: str, steam_url: Optional[str] = None,
                     script: Optional[str] = None, video_start_time: int = 10,
                     interactive_script: bool = True) -> bool:
        """
        Create shorts video with all processing steps
        
        Args:
            game_name: Name of the game
            steam_url: Steam store URL (optional)
            script: Custom script text (optional)
            video_start_time: Start time for background video
            interactive_script: Whether to prompt for script input
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"[START] Starting shorts creation for: {game_name}")
            
            # Update catalog
            self.catalog_manager.update_game_entry(game_name, steam_url, "started")
            
            # Step 1: Download assets
            logger.info("[STEP 1] Downloading game assets...")
            assets_dir, metadata = self.asset_manager.download_game_assets(game_name, steam_url)
            if not assets_dir:
                logger.error("[ERROR] Failed to download assets")
                self.catalog_manager.update_game_entry(game_name, steam_url, "failed", error="asset_download_failed")
                return False
            
            self.catalog_manager.update_game_entry(game_name, steam_url, "assets_downloaded")
            
            # Step 2: Get or create script
            logger.info("[STEP 2] Processing script...")
            if not script:
                script = self._get_script(game_name, metadata, interactive_script)
            
            if not script:
                logger.error("[ERROR] No script available")
                self.catalog_manager.update_game_entry(game_name, steam_url, "failed", error="no_script")
                return False
            
            # Save script
            self._save_script(game_name, script)
            
            # Step 3: Generate TTS audio
            logger.info("[STEP 3] Generating TTS audio...")
            success, audio_path, duration = self.tts_processor.generate_audio(script, game_name)
            if not success:
                logger.error("[ERROR] TTS generation failed")
                self.catalog_manager.update_game_entry(game_name, steam_url, "failed", error="tts_failed")
                return False
            
            # Step 4: Prepare media files
            logger.info("[STEP 4] Preparing media files...")
            images = self.asset_manager.get_image_files(assets_dir)
            if len(images) < 3:
                logger.error("[ERROR] Not enough images available")
                self.catalog_manager.update_game_entry(game_name, steam_url, "failed", error="insufficient_images")
                return False
            
            videos = self.asset_manager.get_video_files(assets_dir)
            video_path = videos[0] if videos else None
            
            # Step 5: Create video
            logger.info("[STEP 5] Creating video...")
            video_mode = self._get_video_mode()
            output_video = self.video_processor.create_video(
                images=images,
                audio_path=audio_path,
                game_name=game_name,
                video_path=video_path,
                video_start_time=video_start_time,
                video_mode=video_mode
            )
            
            if not output_video:
                logger.error("[ERROR] Video creation failed")
                self.catalog_manager.update_game_entry(game_name, steam_url, "failed", error="video_creation_failed")
                return False
            
            # Step 6: Add captions (if enabled)
            final_video = output_video
            if self.mode == "beautiful_captions":
                logger.info("[STEP 6] Adding beautiful captions...")
                captioned_video = output_video.replace(".mp4", "_beautiful_captions.mp4")
                
                if self.caption_manager.add_captions_to_video(output_video, captioned_video, script):
                    final_video = captioned_video
                    # Clean up intermediate file
                    try:
                        Path(output_video).unlink()
                    except:
                        pass
                else:
                    logger.warning("[WARNING] Caption addition failed, using video without captions")
            
            # Step 7: Cleanup and finalize
            logger.info("[STEP 7] Cleaning up...")
            self.tts_processor.cleanup_audio_file(audio_path)
            
            # Update catalog
            file_size = Path(final_video).stat().st_size / (1024*1024)
            self.catalog_manager.update_game_entry(
                game_name, steam_url, "completed",
                output_video=final_video,
                file_size_mb=file_size,
                duration_seconds=duration,
                mode=self.mode
            )
            
            # Success!
            logger.info(f"[SUCCESS] Video created: {final_video}")
            logger.info(f"[INFO] File size: {file_size:.1f}MB, Duration: {duration:.1f}s")
            
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Shorts creation failed: {e}")
            self.catalog_manager.update_game_entry(game_name, steam_url, "failed", error=str(e))
            return False
    
    def _get_script(self, game_name: str, metadata: dict, interactive: bool) -> Optional[str]:
        """Get script from various sources"""
        # Try to load existing script
        script = self._load_existing_script(game_name)
        if script:
            logger.info("[INFO] Using existing script")
            return script
        
        # Interactive input if enabled
        if interactive:
            return self._get_interactive_script(game_name, metadata)
        
        # Auto-generate script
        return self._generate_default_script(game_name, metadata)
    
    def _load_existing_script(self, game_name: str) -> Optional[str]:
        """Load existing script for game"""
        safe_name = create_safe_name(game_name)
        games_dir = config.get_directory("games")
        
        script_files = [
            games_dir / safe_name / "script.json",
            games_dir / safe_name / "script_4x.json"
        ]
        
        for script_file in script_files:
            if script_file.exists():
                try:
                    with open(script_file, 'r', encoding='utf-8') as f:
                        script_data = json.load(f)
                    return script_data.get("script", "")
                except Exception as e:
                    logger.warning(f"Failed to load script from {script_file}: {e}")
        
        return None
    
    def _get_interactive_script(self, game_name: str, metadata: dict) -> Optional[str]:
        """Get script through interactive input"""
        print(f"\n[SCRIPT INPUT] FOR {game_name.upper()}")
        print("=" * 50)
        
        if metadata:
            print("[GAME INFO]")
            if metadata.get('description'):
                print(f"   Description: {metadata['description'][:100]}...")
            if metadata.get('genres'):
                print(f"   Genres: {', '.join(metadata['genres'][:3])}")
            if metadata.get('developers'):
                print(f"   Developer: {', '.join(metadata['developers'][:2])}")
        
        print("\n[SCRIPT GUIDELINES]")
        print(f"   Target: {config.get('script.max_words', 100)} words ({config.get('script.target_duration', 35)} seconds)")
        print("   Structure: Hook -> Core Content -> Call-to-Action")
        print("   Focus on unique features and gameplay")
        print("   End with engagement question")
        
        print(f"\n[INPUT] Please provide your script for {game_name}:")
        print("   (Press Enter twice when finished, or type 'default' for auto-generated)")
        
        script_lines = []
        empty_lines = 0
        
        try:
            while True:
                line = input()
                if line.strip() == "":
                    empty_lines += 1
                    if empty_lines >= 2:
                        break
                else:
                    empty_lines = 0
                    script_lines.append(line)
        except KeyboardInterrupt:
            print("\n[CANCELLED] Script input cancelled")
            return None
        
        user_script = "\n".join(script_lines).strip()
        
        if user_script.lower() == "default" or not user_script:
            return self._generate_default_script(game_name, metadata)
        
        # Show script stats
        word_count = len(user_script.split())
        duration = self.tts_processor.estimate_duration(user_script)
        print(f"\n[STATS] Script Stats: {word_count} words, ~{duration:.1f} seconds")
        
        return user_script
    
    def _generate_default_script(self, game_name: str, metadata: dict) -> str:
        """Generate default script based on game info"""
        # Special cases for known games
        if "elden ring" in game_name.lower():
            return ("Elden Ring Nightreign brings the legendary Souls experience to co-op perfection. "
                   "Team up with friends to conquer the Lands Between in this groundbreaking multiplayer expansion. "
                   "Face massive bosses together, explore interconnected worlds, and experience FromSoftware's masterpiece like never before. "
                   "Every death teaches, every victory feels earned. This is the co-op Souls adventure fans have dreamed of. "
                   "What's your favorite co-op challenge? Follow for more epic gaming content!")
        
        # Generic template
        genres = metadata.get('genres', []) if metadata else []
        if len(genres) >= 2:
            genre_text = f"combining {genres[0]} and {genres[1]}"
        elif len(genres) == 1:
            genre_text = f"delivering amazing {genres[0]}"
        else:
            genre_text = "delivering incredible gameplay"
        
        script = (f"{game_name} pushes gaming boundaries by {genre_text} in ways you've never experienced. "
                 f"With stunning visuals, innovative mechanics, and endless possibilities for adventure, "
                 f"this is a game that rewards creativity and skill. Whether you prefer solo challenges or multiplayer action, "
                 f"every session brings something new to discover. {game_name} is available now. "
                 f"What game should I cover next? Follow for daily gaming discoveries!")
        
        # Adjust length if needed
        max_words = config.get('script.max_words', 100)
        target_duration = config.get('script.target_duration', 35)
        
        if len(script.split()) > max_words:
            script = self.tts_processor.adjust_script_for_duration(script, target_duration)
        
        logger.info("[INFO] Generated default script")
        return script
    
    def _save_script(self, game_name: str, script: str):
        """Save script to games directory"""
        safe_name = create_safe_name(game_name)
        games_dir = config.get_directory("games") / safe_name
        games_dir.mkdir(parents=True, exist_ok=True)
        
        # Save script with metadata
        script_data = {
            "game_name": game_name,
            "script": script,
            "script_type": "user_provided",
            "created_date": datetime.now().isoformat(),
            "word_count": len(script.split()),
            "estimated_duration": self.tts_processor.estimate_duration(script),
            "mode": self.mode
        }
        
        # Choose filename based on mode
        if self.mode == "4x":
            script_file = games_dir / "script_4x.json"
            text_file = games_dir / "script_4x.txt"
        else:
            script_file = games_dir / "script.json"
            text_file = games_dir / "script.txt"
        
        # Save JSON version
        with open(script_file, 'w', encoding='utf-8') as f:
            json.dump(script_data, f, indent=2)
        
        # Save text version
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(script)
        
        logger.info(f"[SAVED] Script saved: {script_file}")
    
    def _get_video_mode(self) -> str:
        """Get video mode string for VideoProcessor"""
        mode_mapping = {
            "4x": "4x_black_bands",
            "beautiful_captions": "standard",
            "standard": "standard"
        }
        return mode_mapping.get(self.mode, "standard")
    
    def show_catalog(self):
        """Display catalog summary"""
        print(self.catalog_manager.show_catalog_summary())

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="PRGAVI - Unified YouTube Shorts Creator")
    parser.add_argument("--game", help="Game name", required=False)
    parser.add_argument("--steam-url", help="Steam page URL")
    parser.add_argument("--script", help="Custom script text")
    parser.add_argument("--script-file", help="Path to script file")
    parser.add_argument("--video-start-time", type=int, default=10, help="Video start time in seconds")
    parser.add_argument("--mode", choices=["standard", "4x", "beautiful_captions"], 
                       default="standard", help="Creation mode")
    parser.add_argument("--no-input", action="store_true", help="Skip interactive script input")
    parser.add_argument("--catalog", action="store_true", help="Show game catalog")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    parser.add_argument("--log-file", help="Log file path")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level, args.log_file)
    
    # Load custom config if provided
    if args.config:
        config_path = Path(args.config)
        if config_path.exists():
            config = Config(str(config_path))
    
    print("PRGAVI - UNIFIED SHORTS CREATOR")
    print("=" * 40)
    print(f"Mode: {args.mode}")
    
    # Show catalog if requested
    if args.catalog:
        creator = PRGAVICreator(args.mode)
        creator.show_catalog()
        return
    
    # Validate required inputs
    if not args.game:
        print("[ERROR] Please provide a game name with --game")
        return
    
    # Extract game name from URL if needed
    if args.steam_url and not validate_steam_url(args.steam_url):
        print("[ERROR] Invalid Steam URL provided")
        return
    
    # Get script from file if provided
    script = args.script
    if args.script_file:
        try:
            with open(args.script_file, 'r', encoding='utf-8') as f:
                script = f.read().strip()
            Path(args.script_file).unlink()  # Clean up temp file
        except Exception as e:
            logger.warning(f"Failed to read script file: {e}")
    
    # Create shorts
    creator = PRGAVICreator(args.mode)
    success = creator.create_shorts(
        game_name=args.game,
        steam_url=args.steam_url,
        script=script,
        video_start_time=args.video_start_time,
        interactive_script=not args.no_input
    )
    
    if success:
        print(f"\n[SUCCESS] Check the output folder for your {args.mode} video.")
    else:
        print(f"\n[ERROR] Failed to create video. Check logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()