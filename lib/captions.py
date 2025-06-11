"""
Caption generation and management for videos
"""

import logging
import tempfile
import subprocess
import numpy as np
import sys
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

from .config import config
from .utils import create_safe_name, cleanup_files

logger = logging.getLogger(__name__)

# Try to import captacity modules for transcription
try:
    captacity_dir = Path("captacity example")
    sys.path.insert(0, str(captacity_dir))
    import segment_parser
    import transcriber
    CAPTACITY_AVAILABLE = True
    logger.info("[CAPTACITY] Modules loaded successfully")
except ImportError:
    logger.warning("[CAPTACITY] Modules not found, will use fallback caption method")
    segment_parser = None
    transcriber = None
    CAPTACITY_AVAILABLE = False

class CaptionManager:
    """Manages caption creation and styling"""
    
    def __init__(self):
        self.temp_dir = config.get_directory("temp")
        self.fonts_dir = config.get_directory("fonts")
        self.caption_settings = config.get("captions", {})
        self.ffmpeg_path = self._find_ffmpeg()
    
    def _find_ffmpeg(self) -> Optional[str]:
        """Find FFmpeg executable"""
        # Check if ffmpeg is in PATH
        ffmpeg_exe = shutil.which("ffmpeg")
        if ffmpeg_exe:
            logger.info(f"[FFMPEG] Found FFmpeg in PATH: {ffmpeg_exe}")
            return ffmpeg_exe
        
        # Check common installation paths on Windows
        common_paths = [
            "C:/ffmpeg/bin/ffmpeg.exe",
            "C:/Program Files/ffmpeg/bin/ffmpeg.exe",
            "C:/Program Files (x86)/ffmpeg/bin/ffmpeg.exe",
            "./ffmpeg.exe",
            "./tools/ffmpeg/ffmpeg.exe"
        ]
        
        for path in common_paths:
            if Path(path).exists():
                logger.info(f"[FFMPEG] Found FFmpeg at: {path}")
                return path
        
        logger.warning("[FFMPEG] FFmpeg not found - captions will use MoviePy audio extraction")
        return None
        
    def add_captions_to_video(self, input_video: str, output_video: str, script: str) -> bool:
        """
        Add beautiful captions with word-by-word highlighting using captacity-style transcription
        
        Args:
            input_video: Path to input video file
            output_video: Path to output video file with captions
            script: Script text for captions
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
            
            logger.info("[CAPTIONS] Adding beautiful captions with word highlighting...")
            
            # Extract audio for transcription
            temp_audio_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
            
            if self.ffmpeg_path:
                # Use FFmpeg if available
                try:
                    subprocess.run([
                        self.ffmpeg_path, '-y', '-i', input_video, temp_audio_file
                    ], capture_output=True, check=True)
                    logger.info("[AUDIO] Extracted audio using FFmpeg")
                except subprocess.CalledProcessError as e:
                    logger.warning(f"[AUDIO] FFmpeg extraction failed: {e}")
                    # Fall back to MoviePy
                    if not self._extract_audio_with_moviepy(input_video, temp_audio_file):
                        return False
            else:
                # Use MoviePy as fallback
                if not self._extract_audio_with_moviepy(input_video, temp_audio_file):
                    return False
            
            # Load video to get dimensions and duration
            video = VideoFileClip(input_video)
            width, height = video.size
            duration = video.duration
            
            # Try transcription or create manual segments
            segments = None
            try:
                if CAPTACITY_AVAILABLE and transcriber and segment_parser:
                    logger.info("[TRANSCRIPTION] Attempting transcription...")
                    segments = transcriber.transcribe_locally(temp_audio_file)
                    if not segments:
                        segments = transcriber.transcribe_with_api(temp_audio_file)
                else:
                    logger.info("[TRANSCRIPTION] Captacity not available, using manual segments")
                    
            except Exception as e:
                logger.warning(f"[WARNING] Transcription failed: {e}")
                segments = None
            
            # If transcription failed and we have a script, create manual segments
            if not segments and script:
                logger.info("[MANUAL] Creating manual transcript from script...")
                words = script.split()
                word_duration = duration / len(words)
                
                word_segments = []
                current_time = 0.0
                
                for word in words:
                    word_segments.append({
                        "word": " " + word,
                        "start": current_time,
                        "end": current_time + word_duration
                    })
                    current_time += word_duration
                
                segments = [{
                    "start": 0.0,
                    "end": duration,
                    "words": word_segments
                }]
            elif not segments:
                logger.error("[ERROR] No transcription or script available for captions")
                return False
            
            # Better fit function for shorter caption segments
            def fits_frame(text):
                # Limit to about 6-8 words per caption for better readability
                word_count = len(text.split())
                char_count = len(text)
                return word_count <= 8 and char_count <= 60
            
            # Parse segments into captions
            if CAPTACITY_AVAILABLE and segment_parser:
                captions = segment_parser.parse(segments=segments, fit_function=fits_frame)
            else:
                # Fallback if segment_parser is not available
                captions = self._create_manual_captions(segments)
            
            logger.info(f"[SEGMENTS] Created {len(captions)} caption segments")
            
            clips = [video]
            
            # Create word-by-word highlighting captions (captacity style)
            for caption in captions:
                words = caption["words"]
                caption_text = caption["text"]
                
                logger.info(f"[PROCESSING] Caption: '{caption_text}' with {len(words)} words")
                
                # Create individual clips for each word highlight
                for i, word in enumerate(words):
                    if i + 1 < len(words):
                        word_end_time = words[i + 1]["start"]
                    else:
                        word_end_time = word["end"]
                    
                    word_start_time = word["start"]
                    word_duration = word_end_time - word_start_time
                    
                    # Create text image with current word highlighted
                    text_img = self._create_text_image_with_word_highlight(
                        text=caption_text,
                        width=width,
                        height=height,
                        current_word_index=i,
                        font_size=self.caption_settings.get("font_size", 70)
                    )
                    
                    # Convert PIL image to numpy array
                    text_array = np.array(text_img)
                    
                    # Create MoviePy ImageClip
                    text_clip = ImageClip(text_array, transparent=True)
                    text_clip = text_clip.set_start(word_start_time)
                    text_clip = text_clip.set_duration(word_duration)
                    text_clip = text_clip.set_position('center')
                    
                    clips.append(text_clip)
            
            # Create final composite video
            logger.info("[COMPOSITE] Creating composite video...")
            final_video = CompositeVideoClip(clips)
            
            # Write output
            logger.info("[EXPORT] Writing video file...")
            final_video.write_videofile(
                output_video,
                fps=config.get("video.fps", 24),
                codec=config.get("video.codec", "libx264"),
                audio_codec=config.get("video.audio_codec", "aac"),
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            # Cleanup
            video.close()
            final_video.close()
            
            # Clean up temp audio file
            try:
                Path(temp_audio_file).unlink()
            except:
                pass
            
            logger.info("[SUCCESS] Beautiful captions added successfully!")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Caption creation failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def _create_manual_captions(self, segments: List[Dict]) -> List[Dict]:
        """Create manual captions when segment_parser is not available"""
        captions = []
        for segment in segments:
            words = segment.get("words", [])
            if words:
                # Group words into caption segments
                current_caption_words = []
                current_text = ""
                
                for word in words:
                    word_text = word.get("word", "").strip()
                    if len(current_text + " " + word_text) <= 60 and len(current_caption_words) < 8:
                        current_caption_words.append(word)
                        current_text += " " + word_text
                    else:
                        # Create caption from current words
                        if current_caption_words:
                            captions.append({
                                "words": current_caption_words,
                                "text": current_text.strip()
                            })
                        # Start new caption
                        current_caption_words = [word]
                        current_text = word_text
                
                # Add remaining words
                if current_caption_words:
                    captions.append({
                        "words": current_caption_words,
                        "text": current_text.strip()
                    })
        
        return captions
    
    def _extract_audio_with_moviepy(self, input_video: str, output_audio: str) -> bool:
        """Extract audio using MoviePy as fallback"""
        try:
            from moviepy.editor import VideoFileClip
            
            logger.info("[AUDIO] Extracting audio using MoviePy...")
            video = VideoFileClip(input_video)
            
            if video.audio is None:
                logger.error("[AUDIO] Video has no audio track")
                video.close()
                return False
            
            video.audio.write_audiofile(output_audio, verbose=False, logger=None)
            video.close()
            logger.info("[AUDIO] Audio extracted using MoviePy")
            return True
            
        except Exception as e:
            logger.error(f"[AUDIO] MoviePy audio extraction failed: {e}")
            return False
    
    def _create_caption_segments(self, script: str, duration: float) -> List[Dict]:
        """Create caption segments from script"""
        # Clean script
        clean_script = script.replace('\n', ' ').strip()
        words = clean_script.split()
        
        if not words:
            return []
        
        # Group words into segments
        max_words_per_segment = 4  # Good for readability
        segments = []
        
        for i in range(0, len(words), max_words_per_segment):
            segment_words = words[i:i + max_words_per_segment]
            segment_text = " ".join(segment_words)
            
            # Calculate timing
            start_time = (i / len(words)) * duration
            end_time = ((i + len(segment_words)) / len(words)) * duration
            
            segments.append({
                "text": segment_text,
                "words": segment_words,
                "start_time": start_time,
                "end_time": end_time,
                "duration": end_time - start_time
            })
        
        return segments
    
    def _create_caption_clip(self, segment: Dict, width: int, height: int, index: int) -> Tuple[Optional[object], Optional[str]]:
        """Create a caption clip for a segment"""
        try:
            from moviepy.editor import ImageClip
            
            # Create text image for each word highlight
            segment_clips = []
            temp_files = []
            
            words = segment["words"]
            word_duration = segment["duration"] / len(words)
            
            for word_index, word in enumerate(words):
                # Create text image with current word highlighted
                text_img = self._create_text_image_with_highlight(
                    segment["text"], width, height, word_index
                )
                
                # Save temporary image
                temp_path = self.temp_dir / f"caption_{index}_{word_index}.png"
                temp_path.parent.mkdir(parents=True, exist_ok=True)
                text_img.save(temp_path)
                temp_files.append(str(temp_path))
                
                # Create clip for this word
                word_start = segment["start_time"] + (word_index * word_duration)
                word_end = word_start + word_duration
                
                word_clip = ImageClip(str(temp_path), duration=word_duration)
                word_clip = word_clip.set_start(word_start)
                word_clip = word_clip.set_position('center')
                
                segment_clips.append(word_clip)
            
            # Return the first clip as representative (in real implementation, 
            # you'd return a composite of all word clips)
            return segment_clips[0] if segment_clips else None, temp_files[0] if temp_files else None
            
        except Exception as e:
            logger.error(f"Error creating caption clip: {e}")
            return None, None
    
    def _create_text_image_with_word_highlight(self, text: str, width: int, height: int, 
                                             current_word_index: int, font_size: int = 70) -> Image.Image:
        """Create text image with captacity-style word highlighting"""
        # Create transparent image
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Try to use a system font (matching old implementation)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        # Split text into words
        words = text.split()
        
        # Calculate text layout with line breaks (matching old implementation)
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
        
        # Limit to 1 line max (captacity style)
        lines = lines[:1]
        
        # Calculate vertical positioning (bottom part of IMAGE SECTION)
        # Video layout: 60% images at top, 40% video at bottom
        image_section_height = int(height * 0.6)  # Top 60% is for images
        line_height = font_size + 15
        total_height = len(lines) * line_height
        padding_from_bottom = 40  # Small padding from bottom of image section
        start_y = image_section_height - total_height - padding_from_bottom  # Bottom of image section
        
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
                # Determine colors (captacity style)
                if word_counter == current_word_index:
                    main_color = (255, 255, 0, 255)  # Yellow for current word
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
    
    def _load_font(self) -> ImageFont.ImageFont:
        """Load appropriate font for captions"""
        font_size = self.caption_settings.get("font_size", 80)
        
        # Try custom font first
        font_path = self.fonts_dir / "Roboto-Bold.ttf"
        if font_path.exists():
            try:
                return ImageFont.truetype(str(font_path), font_size)
            except Exception:
                pass
        
        # Try system fonts
        system_fonts = ["arial.ttf", "Arial.ttf", "C:/Windows/Fonts/arial.ttf"]
        for font_name in system_fonts:
            try:
                return ImageFont.truetype(font_name, font_size)
            except Exception:
                continue
        
        # Fallback to default
        return ImageFont.load_default()
    
    def _layout_text(self, words: List[str], width: int, font: ImageFont.ImageFont, 
                    draw: ImageDraw.ImageDraw) -> List[str]:
        """Layout text into lines that fit the width"""
        lines = []
        current_line = ""
        max_line_count = self.caption_settings.get("line_count", 1)
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            line_width = bbox[2] - bbox[0]
            
            if line_width <= width * 0.9:  # Leave some margin
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                    if len(lines) >= max_line_count:
                        break
                current_line = word
        
        if current_line and len(lines) < max_line_count:
            lines.append(current_line)
        
        return lines[:max_line_count]
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]
        
        try:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except ValueError:
            return (255, 255, 255)  # Default to white