#!/usr/bin/env python3
"""
Shorts Creator - Compact and Manageable
Create professional short-form videos with AI narration and captions
"""

import os
import sys
import logging
import argparse
import subprocess
import json
import time
import requests
from pathlib import Path
import shutil
from PIL import Image, ImageDraw, ImageFont
import random
import yt_dlp
from bs4 import BeautifulSoup
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def create_project_structure():
    """Create organized project folder structure"""
    folders = [
        "games",           # Game-specific scripts and configs
        "assets",          # Downloaded game assets
        "output",          # Final videos
        "temp",           # Temporary files
        "catalog"         # Game catalog and records
    ]
    
    for folder in folders:
        Path(folder).mkdir(exist_ok=True)
    
    logger.info("✅ Project structure created")

def update_game_catalog(game_name, steam_url, status="started"):
    """Update the game catalog with processing records"""
    catalog_file = Path("catalog/game_catalog.json")
    
    # Load existing catalog
    if catalog_file.exists():
        with open(catalog_file, 'r', encoding='utf-8') as f:
            catalog = json.load(f)
    else:
        catalog = {"games": [], "stats": {"total_games": 0, "completed": 0}}
    
    # Find existing entry or create new one
    game_entry = None
    for game in catalog["games"]:
        if game["name"].lower() == game_name.lower():
            game_entry = game
            break
    
    if not game_entry:
        game_entry = {
            "name": game_name,
            "steam_url": steam_url,
            "safe_name": game_name.lower().replace(' ', '_').replace('-', '_'),
            "created_date": datetime.now().isoformat(),
            "status": status,
            "assets_downloaded": False,
            "video_created": False,
            "processing_history": []
        }
        catalog["games"].append(game_entry)
        catalog["stats"]["total_games"] += 1
    
    # Update status and history
    game_entry["status"] = status
    game_entry["last_updated"] = datetime.now().isoformat()
    game_entry["processing_history"].append({
        "timestamp": datetime.now().isoformat(),
        "status": status
    })
    
    if status == "completed":
        game_entry["video_created"] = True
        catalog["stats"]["completed"] += 1
    
    # Save updated catalog
    catalog_file.parent.mkdir(exist_ok=True)
    with open(catalog_file, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2)
    
    logger.info(f"📊 Catalog updated: {game_name} - {status}")
    return game_entry

def save_game_script(game_name, script, script_type="user_provided"):
    """Save game-specific script in organized games folder"""
    safe_name = game_name.lower().replace(' ', '_').replace('-', '_')
    games_dir = Path("games") / safe_name
    games_dir.mkdir(parents=True, exist_ok=True)
    
    # Save script with metadata
    script_data = {
        "game_name": game_name,
        "script": script,
        "script_type": script_type,
        "created_date": datetime.now().isoformat(),
        "word_count": len(script.split()),
        "estimated_duration": (len(script.split()) / 180) * 60
    }
    
    script_file = games_dir / "script.json"
    with open(script_file, 'w', encoding='utf-8') as f:
        json.dump(script_data, f, indent=2)
    
    # Also save plain text version
    text_file = games_dir / "script.txt"
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(script)
    
    logger.info(f"💾 Script saved: {script_file}")
    return str(games_dir)

def load_game_script(game_name):
    """Load game-specific script if it exists"""
    safe_name = game_name.lower().replace(' ', '_').replace('-', '_')
    script_file = Path("games") / safe_name / "script.json"
    
    if script_file.exists():
        with open(script_file, 'r', encoding='utf-8') as f:
            script_data = json.load(f)
        logger.info(f"✅ Loaded existing script for {game_name}")
        return script_data["script"]
    
    return None

def ensure_dependencies():
    """Ensure all required dependencies are installed"""
    dependencies = ["torch", "torchaudio", "chatterbox", "requests", "Pillow", "moviepy==1.0.3", "captacity"]
    
    missing = []
    for package in dependencies:
        try:
            if package == "moviepy==1.0.3":
                import moviepy
                if moviepy.__version__ != "1.0.3":
                    missing.append(package)
                else:
                    logger.info(f"✅ MoviePy {moviepy.__version__} (compatible with Captacity)")
            else:
                __import__(package.split("==")[0])
                logger.info(f"✅ {package}")
        except ImportError:
            missing.append(package)
    
    if missing:
        logger.info(f"Installing missing dependencies: {missing}")
        for package in missing:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
                logger.info(f"✅ Installed {package}")
            except subprocess.CalledProcessError:
                logger.error(f"❌ Failed to install {package}")
                return False
    
    # Patch torch.load for CPU compatibility
    try:
        import torch
        _original_load = torch.load
        def _patched_load(*args, **kwargs):
            if 'map_location' not in kwargs:
                kwargs['map_location'] = 'cpu' 
            return _original_load(*args, **kwargs)
        torch.load = _patched_load
        logger.info("✅ Patched torch.load for CPU compatibility")
    except ImportError:
        pass
    
    return True

def download_game_assets(game_name, steam_url=None):
    """Download game assets from Steam page and API"""
    try:
        # Create safe directory name
        safe_name = game_name.lower().replace(' ', '_').replace('-', '_')
        assets_dir = Path("assets") / safe_name
        images_dir = assets_dir / "images"
        videos_dir = assets_dir / "videos"
        
        # Create directories
        assets_dir.mkdir(parents=True, exist_ok=True)
        images_dir.mkdir(exist_ok=True)
        videos_dir.mkdir(exist_ok=True)
        
        # Check if we already have assets
        existing_images = len(list(images_dir.glob('*.jpg')))
        if existing_images >= 10:
            logger.info(f"✅ Found {existing_images} existing images for {game_name}")
            update_game_catalog(game_name, steam_url, "assets_ready")
            return str(assets_dir)
        
        if not steam_url:
            logger.warning("⚠️ No Steam URL provided, cannot download assets")
            return create_placeholder_assets(game_name)
        
        logger.info(f"🔄 Downloading assets for {game_name} from Steam...")
        
        # Extract Steam App ID from URL
        import re
        app_id_match = re.search(r'/app/(\d+)/', steam_url)
        if not app_id_match:
            logger.error("❌ Could not extract Steam App ID from URL")
            return create_placeholder_assets(game_name)
        
        app_id = app_id_match.group(1)
        
        # Download via Steam API (most reliable)
        api_url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        
        response = requests.get(api_url, headers=headers)
        data = response.json()
        
        if data and data.get(app_id, {}).get('success', False):
            app_data = data[app_id]['data']
            
            # Download screenshots
            screenshots = app_data.get('screenshots', [])
            for i, screenshot in enumerate(screenshots):
                img_url = screenshot.get('path_full')
                if img_url:
                    file_name = f"screenshot_{i+1:02d}.jpg"
                    destination = images_dir / file_name
                    
                    if not destination.exists():
                        download_file(img_url, destination)
                        time.sleep(0.5)
            
            # Download trailer if available
            movies = app_data.get('movies', [])
            if movies:
                movie_url = movies[0].get('mp4', {}).get('max')
                if movie_url:
                    trailer_path = videos_dir / f"{safe_name}_trailer.mp4"
                    download_file(movie_url, trailer_path)
            
            # Save game metadata
            metadata = {
                "name": app_data.get('name', game_name),
                "app_id": app_id,
                "description": app_data.get('short_description', ''),
                "detailed_description": app_data.get('detailed_description', ''),
                "genres": [genre['description'] for genre in app_data.get('genres', [])],
                "developers": app_data.get('developers', []),
                "publishers": app_data.get('publishers', []),
                "release_date": app_data.get('release_date', {}).get('date', ''),
                "steam_url": steam_url,
                "downloaded_at": datetime.now().isoformat()
            }
            
            metadata_file = assets_dir / "game_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"✅ Downloaded {len(screenshots)} images for {game_name}")
            update_game_catalog(game_name, steam_url, "assets_downloaded")
            return str(assets_dir)
        
        logger.warning("⚠️ Steam API failed, creating placeholder assets")
        return create_placeholder_assets(game_name)
        
    except Exception as e:
        logger.error(f"❌ Asset download failed: {e}")
        return create_placeholder_assets(game_name)

def download_file(url, destination):
    """Download a file with progress indicator"""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, stream=True, headers=headers)
        response.raise_for_status()
        
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
        
        print()  # New line after progress
        logger.info(f"✅ Downloaded: {destination}")
        return True
    except Exception as e:
        logger.error(f"❌ Download failed: {e}")
        return False

def create_placeholder_assets(game_name):
    """Create placeholder assets as fallback"""
    try:
        safe_name = game_name.lower().replace(' ', '_').replace('-', '_')
        assets_dir = Path("assets") / safe_name
        images_dir = assets_dir / "images"
        videos_dir = assets_dir / "videos"
        
        assets_dir.mkdir(parents=True, exist_ok=True)
        images_dir.mkdir(exist_ok=True)
        videos_dir.mkdir(exist_ok=True)
        
        # Create 10 placeholder images
        colors = [(70, 130, 180), (255, 160, 122), (152, 251, 152), (255, 69, 0), (147, 112, 219)]
        
        for i in range(10):
            img = Image.new('RGB', (1920, 1080), colors[i % len(colors)])
            draw = ImageDraw.Draw(img)
            
            # Add text
            try:
                font = ImageFont.truetype("arial.ttf", 120)
            except:
                font = ImageFont.load_default()
            
            text = f"{game_name}\nScreenshot {i+1}"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (1920 - text_width) // 2
            y = (1080 - text_height) // 2
            
            draw.text((x, y), text, fill=(255, 255, 255), font=font)
            
            img_path = images_dir / f"placeholder_{i+1:02d}.jpg"
            img.save(img_path, "JPEG", quality=85)
        
        logger.info(f"✅ Created 10 placeholder images for {game_name}")
        return str(assets_dir)
        
    except Exception as e:
        logger.error(f"❌ Placeholder creation failed: {e}")
        return None

def get_script_input_from_user(game_name, metadata=None):
    """Get script input from user with context"""
    print(f"\n🎮 SCRIPT INPUT FOR {game_name.upper()}")
    print("=" * 50)
    
    if metadata:
        print(f"📊 Game Info:")
        print(f"   🎯 Genres: {', '.join(metadata.get('genres', []))}")
        print(f"   👥 Developer: {', '.join(metadata.get('developers', []))}")
        print(f"   📅 Release: {metadata.get('release_date', 'TBA')}")
        print(f"   📝 Description: {metadata.get('description', '')[:100]}...")
    
    print(f"\n💡 Script Guidelines:")
    print(f"   • Target: 80-100 words (30-35 seconds)")
    print(f"   • Structure: Hook → Core Content → Call-to-Action")
    print(f"   • Focus on unique features and gameplay")
    print(f"   • End with engagement question")
    
    print(f"\n✏️ Please provide your script for {game_name}:")
    print(f"   (Press Enter twice when finished, or type 'default' for auto-generated)")
    
    script_lines = []
    empty_lines = 0
    
    while True:
        line = input()
        if line.strip() == "":
            empty_lines += 1
            if empty_lines >= 2:
                break
        else:
            empty_lines = 0
            script_lines.append(line)
    
    user_script = " ".join(script_lines).strip()
    
    if user_script.lower() == "default" or not user_script:
        # Generate default script
        script = generate_default_script(game_name, metadata)
        script_type = "auto_generated"
        print(f"\n📝 Using auto-generated script")
    else:
        script = user_script
        script_type = "user_provided"
        print(f"\n📝 Using your custom script")
    
    word_count = len(script.split())
    duration = (word_count / 180) * 60
    
    print(f"\n📊 Script Stats:")
    print(f"   📝 {word_count} words")
    print(f"   ⏱️ ~{duration:.1f} seconds estimated")
    print(f"   📜 Preview: \"{script[:80]}...\"")
    
    return script, script_type

def generate_default_script(game_name, metadata=None):
    """Generate default script based on game info"""
    # Enhanced scripts based on game type
    if "elden ring" in game_name.lower():
        return "Elden Ring Nightreign brings the legendary Souls experience to co-op perfection. Team up with friends to conquer the Lands Between in this groundbreaking multiplayer expansion. Face massive bosses together, explore interconnected worlds, and experience FromSoftware's masterpiece like never before. Every death teaches, every victory feels earned. This is the co-op Souls adventure fans have dreamed of. Elden Ring Nightreign is coming soon. What's your favorite co-op challenge? Follow for more epic gaming content!"
    
    # Generic template for other games
    genres = metadata.get('genres', []) if metadata else []
    genre_text = f"combining {genres[0]} and {genres[1]}" if len(genres) >= 2 else "delivering incredible gameplay"
    
    return f"{game_name} pushes gaming boundaries by {genre_text} in ways you've never experienced. With stunning visuals, innovative mechanics, and endless possibilities for adventure, this is a game that rewards creativity and skill. Whether you prefer solo challenges or multiplayer action, every session brings something new to discover. {game_name} is available now. What game should I cover next? Follow for daily gaming discoveries!"

def create_tts_audio(script, output_path):
    """Generate TTS audio using Chatterbox"""
    try:
        from chatterbox.tts import ChatterboxTTS
        import torch
        import torchaudio
        
        logger.info("🔊 Generating TTS audio...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        model = ChatterboxTTS.from_pretrained(device=device)
        
        # Generate audio with consistent settings
        wav = model.generate(script, exaggeration=0.3, cfg_weight=0.5, temperature=0.85)
        
        # Save audio
        torchaudio.save(output_path, wav, model.sr)
        
        # Get duration
        info = torchaudio.info(output_path)
        duration = info.num_frames / info.sample_rate
        
        logger.info(f"✅ TTS audio created: {duration:.1f}s")
        return True, duration
        
    except Exception as e:
        logger.error(f"❌ TTS generation failed: {e}")
        return False, 0

def prepare_images(assets_dir, count=15):
    """Get best images for video"""
    images_dir = Path(assets_dir) / "images"
    
    # Get all images
    all_images = []
    for pattern in ["*.jpg", "*.png"]:
        for img_file in images_dir.glob(pattern):
            if img_file.stat().st_size > 30000:  # Min 30KB
                all_images.append(str(img_file))
    
    # Sort by file size (bigger = better quality)
    all_images.sort(key=lambda x: Path(x).stat().st_size, reverse=True)
    
    # Return top images
    selected = all_images[:count]
    logger.info(f"📸 Selected {len(selected)} images")
    return selected

def create_video_with_moviepy(images, video_path, audio_path, output_path, video_start_time=10):
    """Create video using MoviePy 1.0.3"""
    try:
        from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
        import torchaudio
        
        logger.info("🎬 Creating video with MoviePy...")
        
        # Get audio duration
        info = torchaudio.info(audio_path)
        audio_duration = info.num_frames / info.sample_rate
        
        # Load audio
        audio_clip = AudioFileClip(audio_path)
        
        # Video dimensions
        width, height = 1080, 1920
        top_height = int(height * 0.6)  # 60% for images
        bottom_height = height - top_height  # 40% for video
        
        # Create image slideshow
        image_duration = max(3.0, (audio_duration + 3) / len(images))
        top_clips = []
        
        for i, img_path in enumerate(images):
            img_clip = ImageClip(img_path, duration=image_duration)
            img_clip = img_clip.resize(height=top_height)
            
            # Center crop if too wide
            if img_clip.w > width:
                x1 = (img_clip.w - width) / 2
                x2 = (img_clip.w + width) / 2
                img_clip = img_clip.crop(x1=x1, x2=x2)
            
            # Set start time with overlap
            start_time = i * (image_duration * 0.8)
            img_clip = img_clip.set_start(start_time)
            top_clips.append(img_clip)
        
        # Combine image clips
        top_section = CompositeVideoClip(top_clips, size=(width, top_height))
        top_section = top_section.set_duration(audio_duration + 2)
        
        # Process video
        if video_path and Path(video_path).exists():
            video_clip = VideoFileClip(video_path)
            
            # Start at specified time
            if video_clip.duration > video_start_time:
                video_clip = video_clip.subclip(video_start_time)
                logger.info(f"✅ Started video at {video_start_time} seconds")
            
            # Loop if needed
            if video_clip.duration < audio_duration + 5:
                loop_count = int((audio_duration + 5) / video_clip.duration) + 1
                video_clip = concatenate_videoclips([video_clip] * loop_count)
            
            # Resize and position
            video_clip = video_clip.resize(height=bottom_height)
            if video_clip.w > width:
                x1 = (video_clip.w - width) / 2
                x2 = (video_clip.w + width) / 2
                video_clip = video_clip.crop(x1=x1, x2=x2)
            
            video_clip = video_clip.set_position(('center', top_height))
            video_clip = video_clip.set_duration(audio_duration + 2)
            video_clip = video_clip.without_audio()
            
            # Combine sections
            final_video = CompositeVideoClip([top_section, video_clip], size=(width, height))
        else:
            # Images-only version if no video file
            final_video = top_section.resize((width, height))
        
        final_video = final_video.set_duration(audio_duration).set_audio(audio_clip)
        
        # Export video
        logger.info("💾 Exporting video...")
        final_video.write_videofile(
            str(output_path),
            fps=30,
            codec='libx264',
            audio_codec='aac',
            preset='faster'
        )
        
        # Cleanup
        audio_clip.close()
        if 'video_clip' in locals():
            video_clip.close()
        final_video.close()
        for clip in top_clips:
            clip.close()
        
        logger.info("✅ Video created successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Video creation failed: {e}")
        return False

def add_captions_to_video(input_video, output_video):
    """Add captions using Captacity"""
    try:
        import captacity
        
        logger.info("📝 Adding beautiful captions...")
        
        captacity.add_captions(
            video_file=input_video,
            output_file=output_video,
            font_size=130,
            font_color="#FFFFFF",
            stroke_width=4,
            stroke_color="#000000",
            highlight_current_word=True,
            word_highlight_color="#FFD700",
            line_count=2,
            padding=60,
            shadow_strength=2.0,
            print_info=True,
            use_local_whisper="auto"
        )
        
        logger.info("✅ Captions added successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Caption creation failed: {e}")
        return False

def create_shorts(game_name, steam_url=None, video_start_time=10, interactive_script=True):
    """Main function to create shorts video with organized structure"""
    try:
        logger.info(f"🎮 Creating shorts for {game_name}")
        
        # Update catalog
        update_game_catalog(game_name, steam_url, "started")
        
        # Download assets
        assets_dir = download_game_assets(game_name, steam_url)
        if not assets_dir:
            logger.error("❌ Failed to get assets")
            return False
        
        # Load metadata if available
        metadata_file = Path(assets_dir) / "game_metadata.json"
        metadata = None
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        
        # Get script (load existing or get user input)
        script = load_game_script(game_name)
        script_type = "existing"
        
        if not script and interactive_script:
            script, script_type = get_script_input_from_user(game_name, metadata)
            # Save the script
            save_game_script(game_name, script, script_type)
        elif not script:
            script = generate_default_script(game_name, metadata)
            script_type = "auto_generated"
            save_game_script(game_name, script, script_type)
        
        if not script:
            logger.error("❌ Failed to get script")
            return False
        
        # Find video file
        videos_dir = Path(assets_dir) / "videos"
        video_files = list(videos_dir.glob('*.mp4'))
        video_path = str(video_files[0]) if video_files else None
        
        # Create TTS audio
        safe_name = game_name.lower().replace(' ', '_').replace('-', '_')
        audio_path = Path("temp") / f"{safe_name}_audio.wav"
        Path("temp").mkdir(exist_ok=True)
        
        success, duration = create_tts_audio(script, str(audio_path))
        if not success:
            logger.error("❌ Failed to create audio")
            return False
        
        # Prepare images
        images = prepare_images(assets_dir)
        if len(images) < 5:
            logger.error("❌ Not enough images")
            return False
        
        # Create video
        temp_video = Path("output") / f"{safe_name}_temp.mp4"
        final_video = Path("output") / f"{safe_name}_shorts.mp4"
        
        if not create_video_with_moviepy(images, video_path, str(audio_path), str(temp_video), video_start_time):
            logger.error("❌ Failed to create video")
            return False
        
        # Add captions
        if add_captions_to_video(str(temp_video), str(final_video)):
            temp_video.unlink()
        else:
            shutil.move(temp_video, final_video)
        
        # Update catalog
        update_game_catalog(game_name, steam_url, "completed")
        
        # Success!
        file_size = final_video.stat().st_size / (1024*1024)
        logger.info(f"🎉 SUCCESS! Video created: {final_video}")
        logger.info(f"📊 File size: {file_size:.1f}MB")
        logger.info(f"⏱️ Duration: {duration:.1f} seconds")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Shorts creation failed: {e}")
        update_game_catalog(game_name, steam_url, "failed")
        return False

def show_catalog():
    """Display the game catalog"""
    catalog_file = Path("catalog/game_catalog.json")
    
    if not catalog_file.exists():
        print("📊 No games in catalog yet")
        return
    
    with open(catalog_file, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    
    print(f"\n📊 GAME CATALOG")
    print("=" * 50)
    print(f"Total Games: {catalog['stats']['total_games']}")
    print(f"Completed: {catalog['stats']['completed']}")
    print(f"Success Rate: {(catalog['stats']['completed']/catalog['stats']['total_games']*100):.1f}%" if catalog['stats']['total_games'] > 0 else "0%")
    
    print(f"\n🎮 GAMES:")
    for game in catalog["games"]:
        status_icon = "✅" if game["status"] == "completed" else "🔄" if game["status"] in ["started", "processing"] else "❌"
        print(f"   {status_icon} {game['name']} - {game['status']} ({game.get('created_date', '')[:10]})")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Create professional shorts videos with organized structure")
    parser.add_argument("--game", help="Game name")
    parser.add_argument("--steam-url", help="Steam page URL")
    parser.add_argument("--video-start-time", type=int, default=10, help="Start video at second")
    parser.add_argument("--catalog", action="store_true", help="Show game catalog")
    parser.add_argument("--no-input", action="store_true", help="Skip script input prompt")
    
    args = parser.parse_args()
    
    print("🎮 ORGANIZED SHORTS CREATOR")
    print("=" * 40)
    
    # Create project structure
    create_project_structure()
    
    # Show catalog if requested
    if args.catalog:
        show_catalog()
        return
    
    # Require game name
    if not args.game:
        print("❌ Please provide a game name with --game")
        return
    
    # Ensure dependencies
    if not ensure_dependencies():
        print("❌ Failed to install dependencies")
        return
    
    # Create shorts
    create_shorts(args.game, args.steam_url, args.video_start_time, not args.no_input)

if __name__ == "__main__":
    main() 