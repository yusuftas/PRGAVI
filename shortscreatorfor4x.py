#!/usr/bin/env python3
"""
Shorts Creator for 4X Games - No Zoom with Black Bands
Create professional short-form videos for turn-based strategy games with full content visibility
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
import tempfile
import numpy as np

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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Add captacity modules to path
captacity_dir = Path("captacity example")
sys.path.insert(0, str(captacity_dir))

try:
    import segment_parser
    import transcriber
except ImportError:
    logger.warning("⚠️ Captacity modules not found, will use fallback caption method")
    segment_parser = None
    transcriber = None

def create_project_structure():
    """Create necessary directories"""
    folders = ["assets", "output", "temp", "games", "catalog"]
    for folder in folders:
        Path(folder).mkdir(exist_ok=True)
        gitkeep = Path(folder) / ".gitkeep" 
        if not gitkeep.exists():
            gitkeep.write_text("# This directory is part of the project structure\n")
    logger.info("✅ Project structure created")

def create_safe_name(game_name):
    """Create a safe filename from game name by removing illegal characters"""
    return game_name.lower().replace(' ', '_').replace('-', '_').replace(':', '_').replace('/', '_').replace('\\', '_').replace('?', '_').replace('*', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')

def update_game_catalog(game_name, steam_url, status="started"):
    """Update or create game catalog entry"""
    catalog_file = Path("catalog/game_catalog_4x.json")
    
    # Load existing catalog
    if catalog_file.exists():
        try:
            with open(catalog_file, 'r', encoding='utf-8', errors='replace') as f:
                catalog = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning(f"Error reading catalog: {e}, creating new one")
            catalog = {"games": [], "stats": {"total_games": 0, "completed": 0}, "type": "4X_strategy"}
    else:
        catalog = {"games": [], "stats": {"total_games": 0, "completed": 0}, "type": "4X_strategy"}
    
    # Find existing entry or create new one
    game_entry = None
    for game in catalog["games"]:
        if game["name"] == game_name:
            game_entry = game
            break
    
    if not game_entry:
        game_entry = {
            "name": game_name,
            "steam_url": steam_url,
            "safe_name": create_safe_name(game_name),
            "created_date": datetime.now().isoformat(),
            "status": status,
            "assets_downloaded": False,
            "video_created": False,
            "processing_history": [],
            "video_type": "4X_no_zoom"
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
    
    logger.info(f"📊 4X Catalog updated: {game_name} - {status}")
    return game_entry

def save_game_script(game_name, script, script_type="user_provided"):
    """Save game-specific script in organized games folder"""
    safe_name = create_safe_name(game_name)
    games_dir = Path("games") / safe_name
    games_dir.mkdir(parents=True, exist_ok=True)
    
    # Save script with metadata
    script_data = {
        "game_name": game_name,
        "script": script,
        "script_type": script_type,
        "created_date": datetime.now().isoformat(),
        "word_count": len(script.split()),
        "estimated_duration": (len(script.split()) / 180) * 60,
        "video_type": "4X_strategy"
    }
    
    script_file = games_dir / "script_4x.json"
    with open(script_file, 'w', encoding='utf-8') as f:
        json.dump(script_data, f, indent=2)
    
    # Also save plain text version
    text_file = games_dir / "script_4x.txt"
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(script)
    
    logger.info(f"💾 4X Script saved: {script_file}")
    return str(games_dir)

def load_game_script(game_name):
    """Load game-specific script if it exists"""
    safe_name = create_safe_name(game_name)
    script_file = Path("games") / safe_name / "script_4x.json"
    
    if script_file.exists():
        with open(script_file, 'r', encoding='utf-8') as f:
            script_data = json.load(f)
        logger.info(f"✅ Loaded existing 4X script for {game_name}")
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
        original_load = torch.load
        def _patched_load(*args, **kwargs):
            kwargs.setdefault('map_location', 'cpu')
            return original_load(*args, **kwargs)
        torch.load = _patched_load
        logger.info("✅ Torch patched for CPU compatibility")
    except Exception as e:
        logger.warning(f"⚠️ Could not patch torch: {e}")
    
    return True

def download_game_assets(game_name, steam_url=None):
    """Download assets for the game from Steam and YouTube"""
    safe_name = create_safe_name(game_name)
    assets_dir = Path("assets") / safe_name
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    images_dir = assets_dir / "images"
    videos_dir = assets_dir / "videos"
    images_dir.mkdir(exist_ok=True)
    videos_dir.mkdir(exist_ok=True)
    
    logger.info(f"📥 Downloading assets for {game_name}")
    
    # Initialize metadata
    metadata = {
        "game_name": game_name,
        "download_date": datetime.now().isoformat(),
        "images_count": 0,
        "videos_count": 0,
        "steam_url": steam_url
    }
    
    # Download Steam screenshots
    if steam_url:
        try:
            app_id = steam_url.split('/app/')[1].split('/')[0]
            steam_api_url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
            
            response = requests.get(steam_api_url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data[app_id]['success']:
                    game_data = data[app_id]['data']
                    
                    # Update metadata with Steam info
                    metadata.update({
                        "short_description": game_data.get('short_description', ''),
                        "release_date": game_data.get('release_date', {}).get('date', ''),
                        "developers": game_data.get('developers', []),
                        "publishers": game_data.get('publishers', [])
                    })
                    
                    # Download screenshots
                    screenshots = game_data.get('screenshots', [])
                    logger.info(f"📸 Found {len(screenshots)} screenshots")
                    
                    for i, screenshot in enumerate(screenshots[:15]):
                        img_url = screenshot['path_full']
                        img_path = images_dir / f"screenshot_{i+1:02d}.jpg"
                        if download_file(img_url, img_path):
                            metadata["images_count"] += 1
                        time.sleep(0.5)  # Rate limiting
                    
                    logger.info(f"✅ Downloaded {metadata['images_count']} screenshots")
        except Exception as e:
            logger.error(f"❌ Steam download failed: {e}")
    
    # Search for YouTube gameplay videos
    try:
        search_query = f"{game_name} gameplay 4X strategy"
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'default_search': 'ytsearch5:',
            'extract_flat': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(search_query, download=False)
            
            for i, entry in enumerate(search_results['entries'][:3]):
                try:
                    video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                    video_path = videos_dir / f"gameplay_{i+1:02d}.mp4"
                    
                    download_opts = {
                        'format': 'best[height<=1080][ext=mp4]/best[ext=mp4]',
                        'outtmpl': str(video_path),
                        'quiet': True,
                        'no_warnings': True
                    }
                    
                    with yt_dlp.YoutubeDL(download_opts) as ydl_download:
                        ydl_download.download([video_url])
                        
                    if video_path.exists():
                        metadata["videos_count"] += 1
                        logger.info(f"✅ Downloaded: {entry.get('title', 'video')}")
                        break  # Only need one good video
                        
                except Exception as e:
                    logger.warning(f"⚠️ Failed to download video {i+1}: {e}")
                    continue
                    
    except Exception as e:
        logger.error(f"❌ YouTube search failed: {e}")
    
    # Create placeholder assets if needed
    if metadata["images_count"] == 0:
        logger.info("📝 Creating placeholder images...")
        create_placeholder_assets(game_name)
        metadata["images_count"] = 5
    
    # Save metadata
    metadata_file = assets_dir / "metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"✅ Assets downloaded: {metadata['images_count']} images, {metadata['videos_count']} videos")
    return str(assets_dir), metadata

def download_file(url, destination):
    """Download a file from URL to destination"""
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
    except Exception as e:
        logger.error(f"❌ Download failed {destination}: {e}")
        return False

def create_placeholder_assets(game_name):
    """Create placeholder images when real assets aren't available"""
    safe_name = create_safe_name(game_name)
    images_dir = Path("assets") / safe_name / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    
    # Create 5 placeholder images
    for i in range(5):
        img = Image.new('RGB', (1920, 1080), color=(40, 40, 40))
        draw = ImageDraw.Draw(img)
        
        # Try to load a font
        try:
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            font = ImageFont.load_default()
        
        # Add game name and image number
        text = f"{game_name}\n4X Strategy Game\nImage {i+1}"
        
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
    
    logger.info(f"✅ Created 5 placeholder images for {game_name}")

def get_script_input_from_user(game_name, metadata=None):
    """Get script input from user with 4X game suggestions"""
    print(f"\n🎮 Creating script for {game_name} (4X Strategy)")
    print("=" * 50)
    
    if metadata:
        print(f"📝 Game info: {metadata.get('short_description', 'No description available')}")
        print(f"🎯 Release: {metadata.get('release_date', 'Unknown')}")
        if metadata.get('developers'):
            print(f"👥 Developers: {', '.join(metadata['developers'])}")
        print()
    
    print("💡 For 4X strategy games, consider focusing on:")
    print("   • Empire building and expansion")
    print("   • Diplomatic relationships and alliances")
    print("   • Strategic resource management")
    print("   • Technology research and advancement")
    print("   • Military tactics and warfare")
    print("   • Long-term strategic planning")
    print()
    
    print("📝 Enter your script (press Enter twice when done):")
    print("💡 Target 30-60 seconds of narration (150-300 words)")
    print()
    
    lines = []
    empty_lines = 0
    
    while True:
        try:
            line = input()
            if line.strip() == "":
                empty_lines += 1
                if empty_lines >= 2:
                    break
            else:
                empty_lines = 0
                lines.append(line)
        except KeyboardInterrupt:
            print("\n❌ Script input cancelled")
            return None
    
    script = "\n".join(lines).strip()
    
    if not script:
        print("\n⚠️ No script provided. Using auto-generated script...")
        return generate_default_script(game_name, metadata)
    
    print(f"\n✅ Script received ({len(script.split())} words)")
    return script

def generate_default_script(game_name, metadata=None):
    """Generate a default script for 4X strategy games"""
    scripts = [
        f"Dive into the world of {game_name}, where strategic thinking meets empire building. Plan your expansion, manage resources, and forge alliances in this epic 4X strategy experience. Every decision shapes your civilization's destiny. Will you conquer through military might or achieve victory through diplomacy and trade?",
        f"Welcome to {game_name}, the ultimate test of strategic mastery. Build cities, research technologies, and expand your borders in this turn-based strategy epic. Navigate complex diplomatic relationships while managing your economy and military. Your empire's future depends on every tactical choice you make.",
        f"Experience the depth of {game_name}, where civilizations rise and fall based on your strategic vision. Explore vast worlds, develop advanced technologies, and lead your people to greatness. Balance warfare, diplomacy, and resource management in this comprehensive 4X strategy adventure."
    ]
    return random.choice(scripts)

def create_tts_audio(script, output_path):
    """Generate TTS audio using Chatterbox for 4X strategy games"""
    try:
        from chatterbox.tts import ChatterboxTTS
        import torch
        import torchaudio
        
        logger.info("🎙️ Generating TTS audio for 4X strategy...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        model = ChatterboxTTS.from_pretrained(device=device)
        
        # Clean up script for better TTS
        clean_script = script.replace('\n', ' ').strip()
        
        # Generate audio with settings suitable for strategy game narration
        wav = model.generate(clean_script, exaggeration=0.2, cfg_weight=0.4, temperature=0.8)
        
        # Save audio
        torchaudio.save(output_path, wav, model.sr)
        
        # Verify file exists and get duration
        if Path(output_path).exists():
            info = torchaudio.info(output_path)
            duration = info.num_frames / info.sample_rate
            logger.info(f"✅ 4X TTS audio created: {duration:.1f}s")
            return True
        else:
            logger.error("❌ TTS creation failed - no output file")
            return False
            
    except Exception as e:
        logger.error(f"❌ TTS generation failed: {e}")
        return False

def prepare_images(assets_dir, count=15):
    """Prepare images from assets directory, maintaining aspect ratios for 4X games"""
    images_dir = Path(assets_dir) / "images"
    if not images_dir.exists():
        return []
    
    # Get all image files
    image_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp']:
        image_files.extend(images_dir.glob(ext))
    
    if not image_files:
        return []
    
    # Sort and limit
    image_files = sorted(image_files)[:count]
    
    logger.info(f"📸 Prepared {len(image_files)} images for 4X video")
    return [str(img) for img in image_files]

def resize_with_black_bands(image, target_width, target_height):
    """Resize image to fit within target dimensions using black bands, preserving aspect ratio"""
    # Calculate scaling to fit within target dimensions
    original_width, original_height = image.size
    target_ratio = target_width / target_height
    original_ratio = original_width / original_height
    
    if original_ratio > target_ratio:
        # Image is wider - fit to width, add black bands top/bottom
        new_width = target_width
        new_height = int(target_width / original_ratio)
    else:
        # Image is taller - fit to height, add black bands left/right
        new_height = target_height
        new_width = int(target_height * original_ratio)
    
    # Resize image
    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Create black canvas
    final_image = Image.new('RGB', (target_width, target_height), (0, 0, 0))
    
    # Calculate position to center the resized image
    x_offset = (target_width - new_width) // 2
    y_offset = (target_height - new_height) // 2
    
    # Paste resized image onto black canvas
    final_image.paste(resized_image, (x_offset, y_offset))
    
    return final_image

def create_video_with_moviepy_4x(images, video_path, audio_path, output_path, video_start_time=10):
    """Create video using MoviePy with no zoom for 4X games - black bands preserve all content"""
    try:
        from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
        import torchaudio
        
        logger.info("🎬 Creating 4X video with black bands (no zoom)...")
        
        # Get audio duration
        info = torchaudio.info(str(audio_path))
        audio_duration = info.num_frames / info.sample_rate
        
        # Load audio
        audio_clip = AudioFileClip(str(audio_path))
        
        # Video dimensions
        width, height = 1080, 1920
        top_height = int(height * 0.6)  # 60% for images
        bottom_height = height - top_height  # 40% for video
        
        # Create image slideshow with black bands
        image_duration = max(3.0, (audio_duration + 3) / len(images))
        top_clips = []
        
        for i, img_path in enumerate(images):
            # Load and process image with black bands
            pil_image = Image.open(img_path)
            processed_image = resize_with_black_bands(pil_image, width, top_height)
            
            # Save processed image temporarily
            temp_img_path = Path("temp") / f"processed_img_{i}.jpg"
            temp_img_path.parent.mkdir(exist_ok=True)
            processed_image.save(temp_img_path, 'JPEG', quality=95)
            
            # Create image clip
            img_clip = ImageClip(str(temp_img_path), duration=image_duration)
            
            # Set start time with overlap
            start_time = i * (image_duration * 0.8)
            img_clip = img_clip.set_start(start_time)
            top_clips.append(img_clip)
        
        # Combine image clips
        top_section = CompositeVideoClip(top_clips, size=(width, top_height))
        top_section = top_section.set_duration(audio_duration + 2)
        
        # Process video with black bands
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
            
            # Resize video with black bands instead of cropping
            video_aspect = video_clip.w / video_clip.h
            target_aspect = width / bottom_height
            
            if video_aspect > target_aspect:
                # Video is wider - fit to width, add black bands top/bottom
                new_width = width
                new_height = int(width / video_aspect)
                video_clip = video_clip.resize(width=new_width)
            else:
                # Video is taller - fit to height, add black bands left/right
                new_height = bottom_height
                new_width = int(bottom_height * video_aspect)
                video_clip = video_clip.resize(height=new_height)
            
            # Center the video in the bottom section
            video_clip = video_clip.set_position(('center', top_height + (bottom_height - video_clip.h) // 2))
            video_clip = video_clip.set_duration(audio_duration + 2)
            video_clip = video_clip.without_audio()
            
            # Combine sections with black background
            final_video = CompositeVideoClip([
                top_section,
                video_clip
            ], size=(width, height), bg_color=(0, 0, 0))
        else:
            # Images-only version if no video file
            final_video = CompositeVideoClip([top_section], size=(width, height), bg_color=(0, 0, 0))
        
        final_video = final_video.set_duration(audio_duration).set_audio(audio_clip)
        
        # Export video
        logger.info("💾 Exporting 4X video...")
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
        
        # Clean up temporary images
        for i in range(len(images)):
            temp_img_path = Path("temp") / f"processed_img_{i}.jpg"
            if temp_img_path.exists():
                temp_img_path.unlink()
        
        logger.info("✅ 4X Video created successfully with full content visibility!")
        return True
        
    except Exception as e:
        logger.error(f"❌ 4X Video creation failed: {e}")
        return False

def create_text_image_with_word_highlight(text, width, height, current_word_index, font_size=80):
    """Create a text image using PIL with captacity-style word highlighting for 4X games"""
    # Create transparent image
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Try to use a system font
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
    
    # Split text into words
    words = text.split()
    
    # Calculate text layout with line breaks
    lines = []
    current_line = ""
    max_chars_per_line = 30  # Limit characters per line for better readability
    
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if len(test_line) <= max_chars_per_line:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    # Limit to 2 lines max (captacity style)
    lines = lines[:1]
    
    # Calculate vertical positioning (center on screen)
    line_height = font_size + 15
    total_height = len(lines) * line_height
    start_y = (height - total_height) // 2  # Position near bottom like captacity
    
    # Track word index across lines
    word_counter = 0
    
    # Draw each line
    for i, line in enumerate(lines):
        line_words = line.split()
        y_pos = start_y + i * line_height
        
        # Calculate starting x position for centering
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        start_x = (width - line_width) // 2
        
        # Draw word by word with proper highlighting
        word_x = start_x
        for word_idx, word in enumerate(line_words):
            # Determine colors (captacity style with strategic theme)
            if word_counter == current_word_index:
                main_color = (255, 215, 0, 255)  # Gold for current word (strategic theme)
            else:
                main_color = (255, 255, 255, 255)  # White for other words
            
            outline_color = (0, 0, 0, 255)  # Black outline
            
            # Draw shadow/outline first (multiple layers for better effect)
            shadow_offset = 2
            outline_width = 3
            
            # Draw shadow
            for dx in range(-shadow_offset, shadow_offset + 1):
                for dy in range(-shadow_offset, shadow_offset + 1):
                    if dx != 0 or dy != 0:
                        draw.text((word_x + dx, y_pos + dy), word, font=font, fill=(0, 0, 0, 180))
            
            # Draw black outline
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((word_x + dx, y_pos + dy), word, font=font, fill=outline_color)
            
            # Draw main text
            draw.text((word_x, y_pos), word, font=font, fill=main_color)
            
            # Calculate next word position
            word_bbox = draw.textbbox((0, 0), word + " ", font=font)
            word_width = word_bbox[2] - word_bbox[0]
            word_x += word_width
            word_counter += 1
    
    return img

def add_captions_to_video(input_video, output_video, script=None):
    """Add beautiful captions with word-by-word highlighting using PIL for 4X games"""
    try:
        from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
        
        logger.info("📝 Adding captions to 4X video...")
        
        # Load video
        video = VideoFileClip(input_video)
        duration = video.duration
        
        # Use script for captions
        if not script:
            logger.warning("⚠️ No script provided for captions")
            return False
        
        # Clean script
        clean_script = script.replace('\n', ' ').strip()
        words = clean_script.split()
        
        if not words:
            logger.warning("⚠️ No words found in script")
            return False
        
        # Calculate timing
        words_per_second = len(words) / duration
        word_duration = duration / len(words)
        
        logger.info(f"📊 Caption timing: {len(words)} words, {word_duration:.2f}s per word")
        
        # Create caption clips
        caption_clips = []
        
        # Group words into captions (2-4 words per caption for 4X strategy content)
        caption_groups = []
        group_size = 3  # Optimal for strategy game terms
        
        for i in range(0, len(words), group_size):
            group = words[i:i + group_size]
            caption_groups.append(" ".join(group))
        
        def fits_frame(text):
            # Limit to about 3-4 words per caption for better readability of strategy terms
            return len(text.split()) <= 4
        
        # Adjust groups if needed
        final_groups = []
        for group in caption_groups:
            if fits_frame(group):
                final_groups.append(group)
            else:
                # Split long groups
                group_words = group.split()
                for i in range(0, len(group_words), 2):
                    final_groups.append(" ".join(group_words[i:i + 2]))
        
        # Create caption clips
        caption_duration = duration / len(final_groups)
        
        for i, caption_text in enumerate(final_groups):
            start_time = i * caption_duration
            end_time = min((i + 1) * caption_duration, duration)
            
            # Create text image
            text_img = create_text_image_with_word_highlight(
                caption_text, 
                video.w, 
                video.h, 
                current_word_index=0,  # Highlight first word of each caption
                font_size=int(video.h * 0.05)  # Responsive font size
            )
            
            # Save temporary image
            temp_path = Path("temp") / f"caption_{i}.png"
            temp_path.parent.mkdir(exist_ok=True)
            text_img.save(temp_path)
            
            # Create clip
            caption_clip = ImageClip(str(temp_path), duration=end_time - start_time)
            caption_clip = caption_clip.set_start(start_time)
            caption_clip = caption_clip.set_position(('center', 'bottom'))
            
            caption_clips.append(caption_clip)
        
        # Composite final video
        final_video = CompositeVideoClip([video] + caption_clips)
        
        # Export
        logger.info("💾 Exporting 4X video with captions...")
        final_video.write_videofile(
            output_video,
            fps=30,
            codec='libx264',
            audio_codec='aac',
            preset='faster'
        )
        
        # Cleanup
        video.close()
        final_video.close()
        for clip in caption_clips:
            clip.close()
        
        # Remove temporary files
        temp_dir = Path("temp")
        for temp_file in temp_dir.glob("caption_*.png"):
            temp_file.unlink()
        
        logger.info("✅ 4X Captions added successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Caption creation failed: {e}")
        return False

def create_shorts_4x(game_name, steam_url=None, video_start_time=10, interactive_script=True, custom_script_file=None):
    """Main function to create shorts for 4X strategy games with no zoom"""
    try:
        logger.info(f"🚀 Starting 4X shorts creation for: {game_name}")
        
        # Update catalog
        update_game_catalog(game_name, steam_url, "started")
        
        # Check dependencies
        if not ensure_dependencies():
            return False
        
        # Create project structure
        create_project_structure()
        
        # Download assets
        assets_dir, metadata = download_game_assets(game_name, steam_url)
        
        # Get script
        script = None
        
        # Try custom script file first
        if custom_script_file and Path(custom_script_file).exists():
            with open(custom_script_file, 'r', encoding='utf-8') as f:
                script = f.read().strip()
            logger.info(f"✅ Loaded script from {custom_script_file}")
        
        # Try existing script
        if not script:
            script = load_game_script(game_name)
        
        # Interactive or default script
        if not script:
            if interactive_script:
                script = get_script_input_from_user(game_name, metadata)
            else:
                script = generate_default_script(game_name, metadata)
        
        if not script:
            logger.error("❌ No script available")
            return False
        
        # Save script
        save_game_script(game_name, script, "4x_strategy")
        
        # Create TTS audio
        safe_name = create_safe_name(game_name)
        audio_path = Path("temp") / f"{safe_name}_audio.wav"
        if not create_tts_audio(script, str(audio_path)):
            logger.error("❌ TTS creation failed")
            return False
        
        # Prepare images
        images = prepare_images(assets_dir)
        if not images:
            logger.error("❌ No images available")
            return False
        
        # Find video file
        videos_dir = Path(assets_dir) / "videos"
        video_files = list(videos_dir.glob("*.mp4")) if videos_dir.exists() else []
        video_path = str(video_files[0]) if video_files else None
        
        # Create base video with 4X-specific processing (no zoom, black bands)
        base_output = Path("temp") / f"{safe_name}_base.mp4"
        if not create_video_with_moviepy_4x(images, video_path, str(audio_path), str(base_output), video_start_time):
            logger.error("❌ Base video creation failed")
            return False
        
        # Add captions
        final_output = Path("output") / f"{safe_name}_4x_shorts.mp4"
        final_output.parent.mkdir(exist_ok=True)
        
        if not add_captions_to_video(str(base_output), str(final_output), script):
            logger.error("❌ Caption addition failed")
            return False
        
        # Update catalog
        update_game_catalog(game_name, steam_url, "completed")
        
        logger.info(f"🎉 4X Shorts created successfully: {final_output}")
        return True
        
    except Exception as e:
        logger.error(f"❌ 4X Shorts creation failed: {e}")
        update_game_catalog(game_name, steam_url, "failed")
        return False

def show_catalog():
    """Show the 4X games catalog"""
    catalog_file = Path("catalog/game_catalog_4x.json")
    
    if not catalog_file.exists():
        print("📊 No 4X games catalog found")
        return
    
    try:
        with open(catalog_file, 'r', encoding='utf-8') as f:
            catalog = json.load(f)
        
        print("\n🎮 4X STRATEGY GAMES CATALOG")
        print("=" * 40)
        print(f"📊 Total Games: {catalog['stats']['total_games']}")
        print(f"✅ Completed: {catalog['stats']['completed']}")
        print()
        
        for game in catalog["games"]:
            status_emoji = "✅" if game["status"] == "completed" else "⏳" if game["status"] == "started" else "❌"
            print(f"{status_emoji} {game['name']}")
            print(f"   📅 Created: {game['created_date'][:10]}")
            print(f"   🎯 Type: {game.get('video_type', 'Standard')}")
            if game.get("steam_url"):
                print(f"   🔗 Steam: {game['steam_url']}")
            print()
            
    except Exception as e:
        logger.error(f"❌ Error reading catalog: {e}")

def main():
    """Main function for 4X shorts creator"""
    parser = argparse.ArgumentParser(description="Create shorts for 4X strategy games with no zoom")
    parser.add_argument("--game", help="Game name", required=False)
    parser.add_argument("--steam-url", help="Steam store URL", required=False)
    parser.add_argument("--video-start", type=int, default=10, help="Video start time in seconds")
    parser.add_argument("--no-input", action="store_true", help="Use auto-generated script")
    parser.add_argument("--custom-script-file", help="Path to custom script file")
    parser.add_argument("--catalog", action="store_true", help="Show games catalog")
    
    args = parser.parse_args()
    
    if args.catalog:
        show_catalog()
        return
    
    if not args.game:
        print("❌ Game name is required. Use --game parameter or --catalog to view existing games")
        return
    
    success = create_shorts_4x(
        game_name=args.game,
        steam_url=args.steam_url,
        video_start_time=args.video_start,
        interactive_script=not args.no_input,
        custom_script_file=args.custom_script_file
    )
    
    if success:
        print(f"\n🎉 4X Shorts created successfully for {args.game}!")
        print("📁 Check the output folder for your video")
    else:
        print(f"\n❌ Failed to create 4X shorts for {args.game}")

if __name__ == "__main__":
    main() 