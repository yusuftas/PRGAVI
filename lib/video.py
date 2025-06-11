"""
Video processing and creation functionality
"""

import logging
import time
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from PIL import Image

from .config import config
from .utils import create_safe_name, cleanup_files, get_file_size_mb

logger = logging.getLogger(__name__)

class VideoProcessor:
    """Handles video creation and processing"""
    
    def __init__(self):
        self.temp_dir = config.get_directory("temp")
        self.output_dir = config.get_directory("output")
        self.video_settings = config.get("video", {})
        
        # Ensure directories exist
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_video(self, images: List[str], audio_path: str, game_name: str, 
                    video_path: Optional[str] = None, video_start_time: int = 10,
                    video_mode: str = "standard") -> Optional[str]:
        """
        Create video from images and audio
        
        Args:
            images: List of image file paths
            audio_path: Path to audio file
            game_name: Game name for output file naming
            video_path: Optional background video file path
            video_start_time: Start time for background video (seconds)
            video_mode: Video creation mode ("standard", "4x_black_bands", "beautiful_captions")
            
        Returns:
            Path to created video file or None if failed
        """
        try:
            from moviepy.editor import (
                VideoFileClip, AudioFileClip, ImageClip, 
                CompositeVideoClip, concatenate_videoclips
            )
            import torchaudio
            
            logger.info(f"[VIDEO] Creating video for {game_name} in {video_mode} mode")
            
            # Get audio duration
            info = torchaudio.info(audio_path)
            audio_duration = info.num_frames / info.sample_rate
            
            # Load audio
            audio_clip = AudioFileClip(audio_path)
            
            # Video dimensions
            width = self.video_settings.get("width", 1080)
            height = self.video_settings.get("height", 1920)
            
            # Create video based on mode
            if video_mode == "4x_black_bands":
                video_clip = self._create_4x_video_with_black_bands(
                    images, video_path, audio_duration, width, height, video_start_time
                )
            else:
                video_clip = self._create_standard_video(
                    images, video_path, audio_duration, width, height, video_start_time
                )
            
            if not video_clip:
                logger.error("Failed to create video clip")
                return None
            
            # Set audio
            final_video = video_clip.set_duration(audio_duration).set_audio(audio_clip)
            
            # Generate output path
            safe_name = create_safe_name(game_name)
            mode_suffix = f"_{video_mode}" if video_mode != "standard" else ""
            output_filename = f"{safe_name}{mode_suffix}.mp4"
            output_path = self.output_dir / output_filename
            
            # Export video
            logger.info("[EXPORT] Exporting video...")
            final_video.write_videofile(
                str(output_path),
                fps=self.video_settings.get("fps", 30),
                codec=self.video_settings.get("codec", "libx264"),
                audio_codec=self.video_settings.get("audio_codec", "aac"),
                preset=self.video_settings.get("preset", "faster")
            )
            
            # Cleanup
            audio_clip.close()
            video_clip.close()
            final_video.close()
            
            # Log success
            file_size = get_file_size_mb(output_path)
            logger.info(f"[SUCCESS] Video created: {output_path}")
            logger.info(f"[INFO] File size: {file_size:.1f}MB, Duration: {audio_duration:.1f}s")
            
            return str(output_path)
            
        except ImportError as e:
            logger.error(f"[ERROR] MoviePy not available: {e}")
            return None
        except Exception as e:
            logger.error(f"[ERROR] Video creation failed: {e}")
            return None
    
    def _create_standard_video(self, images: List[str], video_path: Optional[str], 
                             duration: float, width: int, height: int, 
                             video_start_time: int) -> Optional[object]:
        """Create standard video with cropping/scaling"""
        try:
            from moviepy.editor import (
                VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
            )
            
            # Calculate layout
            top_height = int(height * 0.6)  # 60% for images
            bottom_height = height - top_height  # 40% for video
            
            # Create image slideshow
            image_clips = self._create_image_slideshow(images, duration, width, top_height)
            
            # Process background video if available
            if video_path and Path(video_path).exists():
                video_clip = VideoFileClip(video_path)
                
                # Start at specified time
                if video_clip.duration > video_start_time:
                    video_clip = video_clip.subclip(video_start_time)
                
                # Loop if needed
                if video_clip.duration < duration + 5:
                    loop_count = int((duration + 5) / video_clip.duration) + 1
                    video_clip = concatenate_videoclips([video_clip] * loop_count)
                
                # Resize and crop for bottom section
                video_clip = video_clip.resize(height=bottom_height)
                if video_clip.w > width:
                    x1 = (video_clip.w - width) / 2
                    x2 = (video_clip.w + width) / 2
                    video_clip = video_clip.crop(x1=x1, x2=x2)
                
                video_clip = video_clip.set_position(('center', top_height))
                video_clip = video_clip.set_duration(duration)
                video_clip = video_clip.without_audio()
                
                # Combine sections
                return CompositeVideoClip([image_clips, video_clip], size=(width, height))
            else:
                # Images only
                return image_clips.resize((width, height))
                
        except Exception as e:
            logger.error(f"Error creating standard video: {e}")
            return None
    
    def _create_4x_video_with_black_bands(self, images: List[str], video_path: Optional[str],
                                        duration: float, width: int, height: int,
                                        video_start_time: int) -> Optional[object]:
        """Create 4X strategy game video with black bands (no cropping)"""
        try:
            from moviepy.editor import (
                VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
            )
            
            # Calculate layout
            top_height = int(height * 0.6)
            bottom_height = height - top_height
            
            # Create image slideshow with black bands
            processed_images = []
            temp_files = []
            
            for i, img_path in enumerate(images):
                try:
                    # Process image with black bands
                    processed_path = self._resize_with_black_bands(
                        img_path, width, top_height, i
                    )
                    if processed_path:
                        processed_images.append(processed_path)
                        temp_files.append(processed_path)
                except Exception as e:
                    logger.warning(f"Failed to process image {img_path}: {e}")
            
            if not processed_images:
                logger.error("No processed images available")
                return None
            
            # Create slideshow from processed images
            image_clips = self._create_image_slideshow(processed_images, duration, width, top_height)
            
            # Process background video with black bands
            if video_path and Path(video_path).exists():
                video_clip = VideoFileClip(video_path)
                
                # Start at specified time
                if video_clip.duration > video_start_time:
                    video_clip = video_clip.subclip(video_start_time)
                
                # Loop if needed
                if video_clip.duration < duration + 5:
                    loop_count = int((duration + 5) / video_clip.duration) + 1
                    video_clip = concatenate_videoclips([video_clip] * loop_count)
                
                # Resize with black bands for bottom section
                video_aspect = video_clip.w / video_clip.h
                target_aspect = width / bottom_height
                
                if video_aspect > target_aspect:
                    # Video is wider - fit to width, add black bands top/bottom
                    new_height = int(width / video_aspect)
                    video_clip = video_clip.resize(width=width)
                    y_offset = (bottom_height - new_height) // 2
                    video_clip = video_clip.set_position(('center', top_height + y_offset))
                else:
                    # Video is taller - fit to height, add black bands left/right
                    new_width = int(bottom_height * video_aspect)
                    video_clip = video_clip.resize(height=bottom_height)
                    x_offset = (width - new_width) // 2
                    video_clip = video_clip.set_position((x_offset, top_height))
                
                video_clip = video_clip.set_duration(duration)
                video_clip = video_clip.without_audio()
                
                # Combine with black background
                final_clip = CompositeVideoClip([
                    image_clips,
                    video_clip
                ], size=(width, height), bg_color=(0, 0, 0))
            else:
                final_clip = CompositeVideoClip([image_clips], size=(width, height), bg_color=(0, 0, 0))
            
            # Schedule cleanup of temporary files
            if temp_files:
                # Note: In production, you'd want to clean these up after video export
                pass
            
            return final_clip
            
        except Exception as e:
            logger.error(f"Error creating 4X video: {e}")
            return None
    
    def _create_image_slideshow(self, images: List[str], duration: float, 
                              width: int, height: int) -> object:
        """Create slideshow from images"""
        try:
            from moviepy.editor import ImageClip, CompositeVideoClip
            
            if not images:
                from moviepy.editor import ColorClip
                return ColorClip(size=(width, height), color=(20, 20, 20), duration=duration)
            
            # Calculate timing
            image_duration = max(3.0, (duration + 3) / len(images))
            clips = []
            
            for i, img_path in enumerate(images):
                try:
                    img_clip = ImageClip(img_path, duration=image_duration)
                    img_clip = img_clip.resize(height=height)
                    
                    # Center crop if too wide
                    if img_clip.w > width:
                        x1 = (img_clip.w - width) / 2
                        x2 = (img_clip.w + width) / 2
                        img_clip = img_clip.crop(x1=x1, x2=x2)
                    
                    # Set timing with overlap
                    start_time = i * (image_duration * 0.8)
                    img_clip = img_clip.set_start(start_time)
                    clips.append(img_clip)
                    
                except Exception as e:
                    logger.warning(f"Failed to process image {img_path}: {e}")
            
            if not clips:
                from moviepy.editor import ColorClip
                return ColorClip(size=(width, height), color=(20, 20, 20), duration=duration)
            
            return CompositeVideoClip(clips, size=(width, height)).set_duration(duration)
            
        except Exception as e:
            logger.error(f"Error creating slideshow: {e}")
            from moviepy.editor import ColorClip
            return ColorClip(size=(width, height), color=(20, 20, 20), duration=duration)
    
    def _resize_with_black_bands(self, image_path: str, target_width: int, 
                               target_height: int, index: int) -> Optional[str]:
        """Resize image with black bands to preserve aspect ratio"""
        try:
            # Load image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Calculate scaling
                original_width, original_height = img.size
                target_ratio = target_width / target_height
                original_ratio = original_width / original_height
                
                if original_ratio > target_ratio:
                    # Image is wider - fit to width
                    new_width = target_width
                    new_height = int(target_width / original_ratio)
                else:
                    # Image is taller - fit to height
                    new_height = target_height
                    new_width = int(target_height * original_ratio)
                
                # Resize image
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Create black canvas
                final_img = Image.new('RGB', (target_width, target_height), (0, 0, 0))
                
                # Center the resized image
                x_offset = (target_width - new_width) // 2
                y_offset = (target_height - new_height) // 2
                final_img.paste(resized_img, (x_offset, y_offset))
                
                # Save processed image
                output_path = self.temp_dir / f"processed_img_{index}_{int(time.time())}.jpg"
                final_img.save(output_path, 'JPEG', quality=95)
                
                return str(output_path)
                
        except Exception as e:
            logger.error(f"Failed to process image {image_path}: {e}")
            return None