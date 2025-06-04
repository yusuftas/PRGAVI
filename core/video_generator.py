import os
import logging
from typing import List, Optional, Dict
from moviepy.editor import *
from moviepy.video.fx import resize
import requests
from PIL import Image
import tempfile
from config import config

logger = logging.getLogger(__name__)

class VideoGenerator:
    """Video generator for creating gaming content videos"""
    
    def __init__(self):
        self.temp_dir = config.TEMP_DIR
        self.output_dir = config.OUTPUT_DIR
        self.target_duration = config.VIDEO_DURATION_SECONDS
        
        # Ensure directories exist
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
    def create_video(self, game_data: Dict, script: str, voiceover_path: str) -> Optional[str]:
        """
        Create a complete video from game data, script, and voiceover
        
        Args:
            game_data: Dictionary containing game information and images
            script: The script text for overlay
            voiceover_path: Path to the generated voiceover audio
            
        Returns:
            Path to the generated video file
        """
        try:
            logger.info(f"Creating video for game: {game_data.get('name', 'Unknown')}")
            
            # Download and prepare images
            image_paths = self._download_game_images(game_data.get('images', []))
            if not image_paths:
                logger.error("No images available for video creation")
                return None
            
            # Load voiceover audio
            audio_clip = AudioFileClip(voiceover_path)
            video_duration = min(audio_clip.duration, self.target_duration)
            
            # Create video slideshow from images
            video_clip = self._create_image_slideshow(image_paths, video_duration)
            
            # Add text overlays
            video_with_text = self._add_text_overlays(video_clip, game_data, script)
            
            # Combine with audio
            final_video = video_with_text.set_audio(audio_clip)
            
            # Generate output filename
            game_name = self._sanitize_filename(game_data.get('name', 'game'))
            output_filename = f"{game_name}_{int(time.time())}.mp4"
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Export video optimized for social media
            final_video.write_videofile(
                output_path,
                fps=30,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=os.path.join(self.temp_dir, 'temp_audio.m4a'),
                remove_temp=True,
                preset='medium',
                ffmpeg_params=[
                    '-crf', '23',  # Good quality/size balance
                    '-aspect', '9:16',  # Vertical format for Shorts/Reels
                    '-movflags', '+faststart'  # Optimize for streaming
                ]
            )
            
            # Cleanup
            video_clip.close()
            video_with_text.close()
            final_video.close()
            audio_clip.close()
            self._cleanup_temp_images(image_paths)
            
            logger.info(f"Video created successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating video: {e}")
            return None
    
    def _download_game_images(self, image_urls: List[str], max_images: int = 5) -> List[str]:
        """Download game images for video creation"""
        downloaded_paths = []
        
        for i, url in enumerate(image_urls[:max_images]):
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                # Save image with temporary filename
                temp_filename = f"game_image_{i}_{int(time.time())}.jpg"
                temp_path = os.path.join(self.temp_dir, temp_filename)
                
                with open(temp_path, 'wb') as f:
                    f.write(response.content)
                
                # Verify and process image
                processed_path = self._process_image(temp_path)
                if processed_path:
                    downloaded_paths.append(processed_path)
                else:
                    os.remove(temp_path)
                    
            except Exception as e:
                logger.warning(f"Failed to download image {url}: {e}")
                continue
        
        logger.info(f"Downloaded {len(downloaded_paths)} images")
        return downloaded_paths
    
    def _process_image(self, image_path: str) -> Optional[str]:
        """Process image for video use (resize, format, etc.)"""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Target size for 9:16 vertical video (1080x1920)
                target_width, target_height = 1080, 1920
                
                # Calculate dimensions to fill frame while maintaining aspect ratio
                img_ratio = img.width / img.height
                target_ratio = target_width / target_height
                
                if img_ratio > target_ratio:
                    # Image is wider, fit to height
                    new_height = target_height
                    new_width = int(target_height * img_ratio)
                else:
                    # Image is taller, fit to width
                    new_width = target_width
                    new_height = int(target_width / img_ratio)
                
                # Resize image
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Crop to center if needed
                if new_width > target_width or new_height > target_height:
                    left = (new_width - target_width) // 2
                    top = (new_height - target_height) // 2
                    right = left + target_width
                    bottom = top + target_height
                    img = img.crop((left, top, right, bottom))
                
                # Save processed image
                processed_path = image_path.replace('.jpg', '_processed.jpg')
                img.save(processed_path, 'JPEG', quality=85)
                
                return processed_path
                
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")
            return None
    
    def _create_image_slideshow(self, image_paths: List[str], duration: float) -> VideoClip:
        """Create a slideshow from images with smooth transitions"""
        if not image_paths:
            # Create a blank clip if no images
            return ColorClip(size=(1080, 1920), color=(20, 20, 20), duration=duration)
        
        # Calculate duration per image
        images_per_clip = duration / len(image_paths)
        transition_duration = 0.5  # Half second transitions
        
        clips = []
        
        for i, image_path in enumerate(image_paths):
            try:
                # Create image clip
                img_clip = ImageClip(image_path)
                img_clip = img_clip.set_duration(images_per_clip)
                
                # Add subtle zoom effect
                zoom_factor = 1.1
                img_clip = img_clip.resize(lambda t: 1 + (zoom_factor - 1) * t / images_per_clip)
                
                # Add crossfade transition (except for first clip)
                if i > 0:
                    img_clip = img_clip.crossfadein(transition_duration)
                
                clips.append(img_clip)
                
            except Exception as e:
                logger.warning(f"Error processing image clip {image_path}: {e}")
                continue
        
        if not clips:
            return ColorClip(size=(1080, 1920), color=(20, 20, 20), duration=duration)
        
        # Concatenate all clips
        final_clip = concatenate_videoclips(clips, method="compose")
        
        # Ensure exact duration
        if final_clip.duration > duration:
            final_clip = final_clip.subclip(0, duration)
        elif final_clip.duration < duration:
            # Loop the video if it's too short
            final_clip = final_clip.loop(duration=duration)
        
        return final_clip
    
    def _add_text_overlays(self, video_clip: VideoClip, game_data: Dict, script: str) -> VideoClip:
        """Add text overlays to video"""
        try:
            # Game title overlay
            title = game_data.get('name', 'Amazing Game')
            title_clip = TextClip(
                title,
                fontsize=60,
                color='white',
                font='Arial-Bold',
                stroke_color='black',
                stroke_width=2
            ).set_position(('center', 100)).set_duration(3)
            
            # Developer overlay
            developer = game_data.get('developer', '')
            dev_clip = None
            if developer:
                dev_clip = TextClip(
                    f"by {developer}",
                    fontsize=30,
                    color='white',
                    font='Arial',
                    stroke_color='black',
                    stroke_width=1
                ).set_position(('center', 200)).set_duration(3)
            
            # Rating overlay (if available)
            rating = game_data.get('rating_score')
            rating_clip = None
            if rating and rating > 0:
                rating_text = f"⭐ {rating:.0f}% Positive"
                rating_clip = TextClip(
                    rating_text,
                    fontsize=35,
                    color='yellow',
                    font='Arial-Bold',
                    stroke_color='black',
                    stroke_width=2
                ).set_position(('center', 1700)).set_duration(video_clip.duration)
            
            # Combine video with text overlays
            clips_to_composite = [video_clip, title_clip]
            
            if dev_clip:
                clips_to_composite.append(dev_clip)
            if rating_clip:
                clips_to_composite.append(rating_clip)
            
            final_video = CompositeVideoClip(clips_to_composite)
            
            return final_video
            
        except Exception as e:
            logger.error(f"Error adding text overlays: {e}")
            return video_clip
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for cross-platform compatibility"""
        import re
        # Remove or replace invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove extra spaces and limit length
        sanitized = '_'.join(sanitized.split())[:50]
        return sanitized
    
    def _cleanup_temp_images(self, image_paths: List[str]):
        """Clean up temporary image files"""
        for path in image_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
                # Also clean up processed versions
                processed_path = path.replace('.jpg', '_processed.jpg')
                if os.path.exists(processed_path):
                    os.remove(processed_path)
            except Exception as e:
                logger.warning(f"Error cleaning up image {path}: {e}")
    
    def create_thumbnail(self, video_path: str) -> Optional[str]:
        """Create a thumbnail from the video"""
        try:
            video = VideoFileClip(video_path)
            # Take frame at 2 seconds
            frame_time = min(2.0, video.duration / 2)
            frame = video.get_frame(frame_time)
            
            # Convert to PIL Image and save
            thumbnail_filename = os.path.splitext(os.path.basename(video_path))[0] + '_thumb.jpg'
            thumbnail_path = os.path.join(self.output_dir, thumbnail_filename)
            
            Image.fromarray(frame).save(thumbnail_path, 'JPEG', quality=85)
            
            video.close()
            logger.info(f"Thumbnail created: {thumbnail_path}")
            return thumbnail_path
            
        except Exception as e:
            logger.error(f"Error creating thumbnail: {e}")
            return None

import time 