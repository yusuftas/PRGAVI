#!/usr/bin/env python3
"""
Add Captions to Existing Video
A standalone script to add Captacity captions to existing video files
"""

import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def patch_moviepy_for_captacity():
    """Patch MoviePy imports for Captacity compatibility with MoviePy 2.x"""
    try:
        # Import the classes from their actual locations in MoviePy 2.x
        from moviepy.video.io.VideoFileClip import VideoFileClip
        from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
        from moviepy.audio.io.AudioFileClip import AudioFileClip  
        from moviepy.video.VideoClip import VideoClip, ImageClip, TextClip
        from moviepy.video.compositing.concatenate import concatenate_videoclips
        
        logger.info("✅ Successfully imported MoviePy 2.x classes")
        
        # Create a fake moviepy.editor module that points to the actual classes
        if 'moviepy.editor' not in sys.modules:
            class FakeEditor:
                pass
            
            # Assign the classes to the fake editor after creation
            fake_editor = FakeEditor()
            fake_editor.VideoFileClip = VideoFileClip
            fake_editor.CompositeVideoClip = CompositeVideoClip
            fake_editor.AudioFileClip = AudioFileClip
            fake_editor.ImageClip = ImageClip
            fake_editor.TextClip = TextClip
            fake_editor.VideoClip = VideoClip
            fake_editor.concatenate_videoclips = concatenate_videoclips
            
            sys.modules['moviepy.editor'] = fake_editor
            
        logger.info("✅ Successfully patched MoviePy imports for Captacity")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to patch MoviePy imports: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def add_captions_with_captacity(input_video, output_video, script_text=None):
    """
    Add captions to video using Captacity with SHORTS_VIDEO_GUIDELINES.md settings
    Based on: https://github.com/unconv/captacity/blob/master/captacity/text_drawer.py
    """
    try:
        # First patch MoviePy imports
        if not patch_moviepy_for_captacity():
            return False
        
        # Import Captacity after patching
        import captacity
        
        logger.info("📝 Adding Captacity word-by-word captions...")
        logger.info(f"🎬 Input video: {input_video}")
        logger.info(f"💾 Output video: {output_video}")
        
        # SHORTS_VIDEO_GUIDELINES.md settings:
        # font_size=130, font_color="yellow", stroke_width=3, stroke_color="black", 
        # shadow_strength=1.0, shadow_blur=0.1, word_highlight_color="red"
        
        captacity.add_captions(
            video_file=str(input_video),
            output_file=str(output_video),
            
            # Caption appearance (from SHORTS_VIDEO_GUIDELINES.md)
            font_size=130,
            font_color="yellow",
            stroke_width=3,
            stroke_color="black",
            
            # Word highlighting for engagement
            highlight_current_word=True,
            word_highlight_color="red",
            
            # Layout settings
            line_count=2,  # Max 2 lines for shorts
            padding=50,    # Padding from edges
            
            # Shadow and effects
            shadow_strength=1.0,
            shadow_blur=0.1,
            
            # Processing options
            print_info=True,           # Show progress
            use_local_whisper="auto",  # Use local Whisper model (we installed it)
            
            # Optional: Custom prompt for better transcription
            initial_prompt="This is gaming content about No Man's Sky, featuring space exploration, planets, and gameplay."
        )
        
        logger.info("✅ Captacity captions added successfully!")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Captacity import failed: {e}")
        logger.error("💡 Make sure Captacity is installed: pip install captacity")
        return False
    except Exception as e:
        logger.error(f"❌ Caption creation failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Main function to add captions to No Man's Sky video"""
    print("🎬 CAPTACITY CAPTION ADDER")
    print("=" * 50)
    
    # Look for No Man's Sky videos (try different naming patterns)
    output_dir = Path("output")
    possible_names = [
        "no_man's_sky_shorts.mp4"
    ]
    
    input_video = None
    for name in possible_names:
        candidate = output_dir / name
        if candidate.exists():
            input_video = candidate
            break
    
    if not input_video:
        logger.error(f"❌ No Man's Sky video not found. Tried: {possible_names}")
        logger.info("💡 Available videos in output folder:")
        if output_dir.exists():
            for video in output_dir.glob("*.mp4"):
                logger.info(f"   📹 {video.name}")
        return False
    
    # Create output filename
    stem = input_video.stem
    output_video = output_dir / f"{stem}_with_captions.mp4"
    
    # Check if output already exists
    if output_video.exists():
        logger.info(f"⚠️ Output video already exists: {output_video}")
        response = input("Do you want to overwrite it? (y/n): ").lower().strip()
        if response != 'y':
            logger.info("❌ Cancelled by user")
            return False
    
    # Get video info
    file_size = input_video.stat().st_size / (1024*1024)
    logger.info(f"📹 Found input video: {input_video}")
    logger.info(f"📊 File size: {file_size:.1f}MB")
    
    # Add captions
    if add_captions_with_captacity(input_video, output_video):
        if output_video.exists():
            output_size = output_video.stat().st_size / (1024*1024)
            logger.info(f"🎉 SUCCESS! Captions added successfully!")
            logger.info(f"📁 Output location: {output_video.absolute()}")
            logger.info(f"📊 Output file size: {output_size:.1f}MB")
            
            logger.info(f"\n✨ Caption Features Added:")
            logger.info(f"   📝 Word-by-word highlighting with Whisper transcription")
            logger.info(f"   🎨 Yellow text with red word highlights")
            logger.info(f"   🖋️ Black stroke outlines for readability")
            logger.info(f"   💫 Shadows and effects for visual depth")
            logger.info(f"   📱 Optimized for YouTube Shorts/TikTok/Instagram")
            
            return True
        else:
            logger.error("❌ Output video was not created")
            return False
    else:
        logger.error("❌ Failed to add captions")
        return False

if __name__ == "__main__":
    main() 