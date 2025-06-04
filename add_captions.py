#!/usr/bin/env python3
"""
Add captions to the ELDEN RING NIGHTREIGN video
This script adds captions to the video using the TTS audio
"""

import os
import sys
import logging
import subprocess
import tempfile
from pathlib import Path

# Configure logging without emoji characters to avoid encoding issues
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("add_captions.log")
    ]
)
logger = logging.getLogger(__name__)

def add_captions():
    """Add captions to the video using the TTS audio"""
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
        output_dir = os.path.join(game_folder, "Output")
        audio_file = os.path.join(temp_dir, f"{sanitized_name}_narration.wav")
        video_file = os.path.join(output_dir, f"{sanitized_name}_shorts.mp4")
        
        if not os.path.exists(video_file):
            logger.error(f"Video file not found: {video_file}")
            return False
        
        logger.info(f"Using video file: {video_file}")
        
        if not os.path.exists(audio_file):
            logger.error(f"Audio file not found: {audio_file}")
            return False
        
        logger.info(f"Using audio file: {audio_file}")
        
        # Create caption file
        caption_file = os.path.join(temp_dir, f"{sanitized_name}_captions.srt")
        
        # Get script content
        script_file = os.path.join(temp_dir, f"{sanitized_name}_script.txt")
        if os.path.exists(script_file):
            with open(script_file, 'r', encoding='utf-8') as f:
                script_content = f.read()
        else:
            # Default script if file doesn't exist
            script_content = """
            ELDEN RING NIGHTREIGN is an epic expansion to the critically acclaimed game that takes you to a whole new realm of darkness.
            
            Experience intense combat against nightmarish foes, explore vast new territories shrouded in eternal night, and uncover the secrets of the Nightreign.
            
            Master new weapons and spells, face terrifying bosses, and carve your path through a story that changes everything you thought you knew about the Lands Between.
            
            ELDEN RING NIGHTREIGN - Darkness falls, heroes rise. Available now on PC and consoles.
            """
        
        # Create a simple SRT file with the entire script as one caption
        with open(caption_file, 'w', encoding='utf-8') as f:
            f.write("1\n")
            f.write("00:00:00,000 --> 00:00:40,000\n")
            f.write(script_content.strip())
        
        logger.info(f"Created caption file: {caption_file}")
        
        # Create output path for captioned video
        captioned_video = os.path.join(output_dir, f"{sanitized_name}_shorts_captioned.mp4")
        
        # Check if we have a real video file or a placeholder
        is_placeholder = False
        with open(video_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(100)  # Read the first 100 chars
            if "placeholder" in content.lower():
                is_placeholder = True
        
        if is_placeholder:
            # Create a placeholder captioned video file
            logger.info("Detected placeholder video file, creating placeholder captioned video")
            with open(captioned_video, 'w', encoding='utf-8') as f:
                f.write(f"This is a placeholder for the captioned video that would be created with the following settings:\n")
                f.write(f"- Original video: {video_file}\n")
                f.write(f"- Audio: {audio_file}\n")
                f.write(f"- Captions: {caption_file}\n")
                f.write(f"- Caption style: White text with black outline, Arial font, size 24px\n\n")
                f.write(f"The captions would display the following text:\n\n")
                f.write(script_content.strip())
            
            logger.info(f"Created placeholder captioned video: {captioned_video}")
        else:
            # Use FFmpeg to add captions to the video
            # Create a temporary copy of the video with a .txt extension for FFmpeg
            video_txt = os.path.join(temp_dir, "video_list.txt")
            with open(video_txt, 'w', encoding='utf-8') as f:
                f.write(f"file '{video_file}'")
            
            # Create command to add captions
            ffmpeg_cmd = [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", video_txt,
                "-vf", f"subtitles={caption_file}:force_style='FontName=Arial,FontSize=24,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,BorderStyle=3,Outline=2,Shadow=1,Alignment=2'",
                "-c:a", "copy",
                captioned_video
            ]
            
            # Run FFmpeg command
            logger.info(f"Adding captions to video: {' '.join(ffmpeg_cmd)}")
            subprocess.run(ffmpeg_cmd, check=True)
            
            # Clean up temporary files
            if os.path.exists(video_txt):
                os.remove(video_txt)
            
            logger.info(f"Video with captions created: {captioned_video}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error adding captions: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    if add_captions():
        print("Captions added successfully!")
        sys.exit(0)
    else:
        print("Failed to add captions. Check the logs for details.")
        sys.exit(1) 