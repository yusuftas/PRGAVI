#!/usr/bin/env python3
"""
Simple caption video creator for ELDEN RING NIGHTREIGN
This script creates a video with the TTS audio we already generated
"""

import os
import sys
import logging
import subprocess
from pathlib import Path

# Configure logging without emoji characters to avoid encoding issues
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("simple_caption.log")
    ]
)
logger = logging.getLogger(__name__)

def create_video():
    """Create a video with the TTS audio we already generated"""
    try:
        # Set paths
        temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
        game_name = "ELDEN RING NIGHTREIGN"
        sanitized_name = game_name.replace(" ", "_")
        
        # Find the game folder
        games_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "GameVids", "Games")
        matching_folders = []
        for folder in os.listdir(games_dir):
            if folder.startswith(f"{sanitized_name}_") and os.path.isdir(os.path.join(games_dir, folder)):
                matching_folders.append(folder)
        
        if not matching_folders:
            logger.error(f"No game folder found for {game_name}")
            return False
        
        # Use the most recent folder
        matching_folders.sort(reverse=True)
        game_folder = os.path.join(games_dir, matching_folders[0])
        logger.info(f"Using game folder: {game_folder}")
        
        # Define paths
        images_dir = os.path.join(game_folder, "Assets", "Images")
        video_dir = os.path.join(game_folder, "Assets", "Video")
        output_dir = os.path.join(game_folder, "Output")
        
        # Find video file
        video_file = None
        for file in os.listdir(video_dir):
            if file.endswith((".mp4", ".avi", ".mov")):
                video_file = os.path.join(video_dir, file)
                break
        
        if not video_file:
            logger.error("No video file found")
            return False
        
        logger.info(f"Using video file: {video_file}")
        
        # Find audio file
        audio_file = os.path.join(temp_dir, f"{sanitized_name}_narration.wav")
        if not os.path.exists(audio_file):
            logger.error(f"Audio file not found: {audio_file}")
            return False
        
        logger.info(f"Using audio file: {audio_file}")
        
        # Create output directory if needed
        os.makedirs(output_dir, exist_ok=True)
        
        # Import required modules
        try:
            import numpy as np
            from PIL import Image
            
            # Set environment variable for ImageMagick
            os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
            if not os.path.exists(os.environ["IMAGEMAGICK_BINARY"]):
                # Try portable version
                os.environ["IMAGEMAGICK_BINARY"] = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)), 
                    "tools", "ImageMagick-7.1.1-47-portable-Q16-HDRI-x64", "magick.exe"
                )
            
            # Import from our local moviepy_editor
            from moviepy_editor import VideoFileClip, AudioFileClip, ImageClip, ColorClip, CompositeVideoClip, concatenate_videoclips
            
            logger.info("Successfully imported required modules")
        except ImportError as e:
            logger.error(f"Error importing modules: {e}")
            return False
        
        # Get image files
        image_files = sorted([str(f) for f in Path(images_dir).glob("*.jpg")] + 
                            [str(f) for f in Path(images_dir).glob("*.png")])
        
        if len(image_files) < 2:
            logger.error(f"Not enough images found in {images_dir}")
            return False
        
        logger.info(f"Found {len(image_files)} images")
        
        # Create output file path
        output_path = os.path.join(output_dir, f"{sanitized_name}_shorts.mp4")
        
        # Create video
        logger.info("Creating video...")
        
        # Load audio to get duration
        audio_clip = AudioFileClip(audio_file)
        duration = audio_clip.duration
        logger.info(f"Audio duration: {duration:.1f} seconds")
        
        # Create clips
        clips = []
        img_duration = duration / len(image_files)
        
        for img_path in image_files:
            try:
                clip = ImageClip(img_path, duration=img_duration)
                clip = clip.resize(width=1080)
                clips.append(clip)
            except Exception as e:
                logger.error(f"Error processing image {img_path}: {e}")
        
        if not clips:
            logger.error("No valid clips created")
            return False
        
        # Create video clip
        video_clip = VideoFileClip(video_file)
        video_clip = video_clip.resize(width=1080)
        
        if video_clip.duration < duration:
            video_clip = video_clip.loop(duration=duration)
        else:
            video_clip = video_clip.subclip(0, duration)
        
        # Create a simple layout
        image_clips = concatenate_videoclips(clips)
        
        background = ColorClip((1080, 1920), color=(0, 0, 0), duration=duration)
        
        image_clips = image_clips.resize(width=1080, height=960).set_position(('center', 0))
        video_clip = video_clip.resize(width=1080, height=960).set_position(('center', 960))
        
        # Composite and add audio
        final_clip = CompositeVideoClip([background, image_clips, video_clip], size=(1080, 1920))
        final_clip = final_clip.set_audio(audio_clip)
        
        # Write video
        logger.info(f"Writing video to: {output_path}")
        final_clip.write_videofile(
            output_path,
            fps=30,
            codec='libx264',
            audio_codec='aac',
            threads=4,
            preset='medium'
        )
        
        logger.info(f"Video created successfully: {output_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error creating video: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    if create_video():
        print("Video created successfully!")
        sys.exit(0)
    else:
        print("Video creation failed. Check the logs for details.")
        sys.exit(1) 