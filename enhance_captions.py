#!/usr/bin/env python3
"""
Enhanced Caption Generator for Shorts Creator
Uses ImageMagick techniques to improve caption appearance
"""

import os
import sys
import logging
import subprocess
import argparse
from pathlib import Path
import tempfile
import json
import time
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def ensure_directory(directory):
    """Ensure a directory exists"""
    Path(directory).mkdir(parents=True, exist_ok=True)

def run_magick_command(cmd):
    """Run an ImageMagick command and handle errors"""
    try:
        result = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"ImageMagick command failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False, e.stderr

def enhance_caption_image(input_path, output_path, config):
    """
    Enhance a caption image using ImageMagick techniques
    
    Args:
        input_path: Path to input caption image
        output_path: Path to output enhanced caption
        config: Dictionary of caption enhancement settings
    """
    # Extract configuration parameters with defaults
    font = config.get('font', 'Roboto-Bold.ttf')
    font_size = config.get('pointsize', 48)
    text_color = config.get('fill', 'white')
    stroke_color = config.get('stroke', 'black')
    stroke_width = config.get('strokewidth', 2)
    gravity = config.get('gravity', 'center')
    bg_color = config.get('background', 'rgba(0,0,0,0.5)')
    padding = config.get('padding', 20)
    kerning = config.get('kerning', 8)
    interword_spacing = config.get('interword-spacing', 10)
    
    # Construct full font path if needed
    if not os.path.isabs(font):
        font_path = str(Path('fonts') / font)
        if not Path(font_path).exists():
            font_path = font  # Fall back to system font
    else:
        font_path = font
    
    # Build ImageMagick command
    cmd = [
        'magick',
        input_path,
        '-font', font_path,
        '-pointsize', str(font_size),
        '-fill', text_color,
        '-stroke', stroke_color,
        '-strokewidth', str(stroke_width),
        '-gravity', gravity,
        '-background', bg_color,
        '-kerning', str(kerning),
        '-interword-spacing', str(interword_spacing),
        '-bordercolor', bg_color,
        '-border', f'{padding}x{padding}',
        output_path
    ]
    
    # Run command
    logger.info(f"Enhancing caption: {input_path} -> {output_path}")
    success, output = run_magick_command(cmd)
    if success:
        logger.info(f"✅ Enhanced caption created: {output_path}")
        return True
    else:
        logger.error(f"❌ Failed to enhance caption: {input_path}")
        return False

def process_captacity_output(captacity_dir, output_dir, config_file=None):
    """
    Process captacity output directory to enhance all caption images
    
    Args:
        captacity_dir: Directory containing captacity output files
        output_dir: Directory to save enhanced captions
        config_file: Path to caption configuration file
    """
    # Read configuration
    config = {}
    if config_file and Path(config_file).exists():
        logger.info(f"Reading caption configuration from: {config_file}")
        try:
            # Read from text file with <caption> tags
            with open(config_file, 'r') as f:
                content = f.read()
                # Extract content between <caption> tags
                match = re.search(r'<caption>(.*?)</caption>', content, re.DOTALL)
                if match:
                    caption_text = match.group(1)
                    # Parse key=value pairs
                    for line in caption_text.splitlines():
                        line = line.strip()
                        if '=' in line:
                            key, value = line.split('=', 1)
                            config[key.strip()] = value.strip()
                    logger.info(f"Loaded configuration: {config}")
                else:
                    logger.warning("No <caption> tags found in config file")
        except Exception as e:
            logger.error(f"Error reading configuration file: {e}")
    
    # Ensure output directory exists
    ensure_directory(output_dir)
    
    # Find all caption images
    caption_dir = Path(captacity_dir)
    caption_files = list(caption_dir.glob('*.png'))
    
    if not caption_files:
        logger.warning(f"No caption images found in: {captacity_dir}")
        return False
    
    logger.info(f"Found {len(caption_files)} caption images to enhance")
    
    # Process each caption
    for caption_file in caption_files:
        output_file = Path(output_dir) / caption_file.name
        enhance_caption_image(str(caption_file), str(output_file), config)
    
    logger.info(f"✅ Enhanced {len(caption_files)} captions")
    return True

def main():
    parser = argparse.ArgumentParser(description="Enhance captions using ImageMagick techniques")
    parser.add_argument("--input", help="Input directory containing captacity output", default="temp/captions")
    parser.add_argument("--output", help="Output directory for enhanced captions", default="temp/enhanced_captions")
    parser.add_argument("--config", help="Caption configuration file", default="temp/caption_config.txt")
    
    args = parser.parse_args()
    
    print("🖼️ CAPTION ENHANCEMENT USING IMAGEMAGICK")
    print("=" * 60)
    
    # Check for ImageMagick
    try:
        result = subprocess.run(
            ["magick", "--version"], 
            capture_output=True, 
            text=True, 
            check=False
        )
        if result.returncode == 0 and "ImageMagick" in result.stdout:
            logger.info(f"✅ ImageMagick found: {result.stdout.splitlines()[0]}")
        else:
            logger.error("❌ ImageMagick not found or not working correctly")
            print("Please ensure ImageMagick is installed and in your PATH")
            return
    except Exception as e:
        logger.error(f"❌ Error checking for ImageMagick: {e}")
        print("Please ensure ImageMagick is installed and in your PATH")
        return
    
    # Process captions
    if process_captacity_output(args.input, args.output, args.config):
        print(f"\n🎉 SUCCESS! Enhanced captions created in: {args.output}")
    else:
        print("\n❌ Failed to enhance captions")

if __name__ == "__main__":
    main() 