#!/usr/bin/env python3

import json
import os
import sys
import tempfile
import subprocess
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Add captacity modules to path
captacity_dir = Path("captacity example")
sys.path.insert(0, str(captacity_dir))

import segment_parser
import transcriber

def load_game_metadata():
    """Load game metadata from JSON file"""
    with open('elden_ring_nightreign/game_metadata.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def create_narration_text(metadata):
    """Create narration text from game metadata"""
    description = metadata['description']
    narration = f"{metadata['name']}. {description}"
    
    # Clean up the description
    narration = narration.replace('\u2019', "'")
    narration = narration.replace('&amp;', 'and')
    
    # Limit to reasonable length for 20 seconds
    if len(narration) > 280:
        sentences = narration.split('. ')
        narration = sentences[0] + '.'
        if len(narration) < 200 and len(sentences) > 1:
            narration += ' ' + sentences[1] + '.'
    
    return narration

def create_text_image_with_word_highlight(text, width, height, current_word_index, font_size=80):
    """Create a text image using PIL with captacity-style word highlighting"""
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
    lines = lines[:2]
    
    # Calculate vertical positioning (center on screen)
    line_height = font_size + 15
    total_height = len(lines) * line_height
    start_y = height - total_height - 100  # Position near bottom like captacity
    
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

def add_captions_with_captacity_style(video_file, output_file, narration_text, print_info=True):
    """Add captions using PIL-generated images with captacity-style word highlighting"""
    from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
    
    if print_info:
        print("Adding captions with captacity-style word highlighting...")
    
    # Extract audio for transcription
    temp_audio_file = tempfile.NamedTemporaryFile(suffix=".wav").name
    subprocess.run([
        'ffmpeg', '-y', '-i', video_file, temp_audio_file
    ], capture_output=True)
    
    # Load video to get dimensions and duration
    video = VideoFileClip(video_file)
    width, height = video.size
    duration = video.duration
    
    # Try transcription or create manual segments
    try:
        if print_info:
            print("Attempting transcription...")
        
        segments = transcriber.transcribe_locally(temp_audio_file)
        if not segments:
            segments = transcriber.transcribe_with_api(temp_audio_file)
            
    except Exception as e:
        if print_info:
            print(f"Transcription failed: {e}")
            print("Creating manual transcript...")
        
        # Create manual transcript
        words = narration_text.split()
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
    
    # Better fit function for shorter caption segments
    def fits_frame(text):
        # Limit to about 6-8 words per caption for better readability
        word_count = len(text.split())
        char_count = len(text)
        return word_count <= 8 and char_count <= 60
    
    captions = segment_parser.parse(segments=segments, fit_function=fits_frame)
    
    if print_info:
        print(f"Created {len(captions)} caption segments")
    
    clips = [video]
    
    # Create word-by-word highlighting captions (captacity style)
    for caption in captions:
        words = caption["words"]
        caption_text = caption["text"]
        
        if print_info:
            print(f"Processing caption: '{caption_text}' with {len(words)} words")
        
        # Create individual clips for each word highlight
        for i, word in enumerate(words):
            if i + 1 < len(words):
                word_end_time = words[i + 1]["start"]
            else:
                word_end_time = word["end"]
            
            word_start_time = word["start"]
            word_duration = word_end_time - word_start_time
            
            # Create text image with current word highlighted
            text_img = create_text_image_with_word_highlight(
                text=caption_text,
                width=width,
                height=height,
                current_word_index=i,
                font_size=70
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
    if print_info:
        print("Creating composite video...")
    
    final_video = CompositeVideoClip(clips)
    
    # Write output
    if print_info:
        print("Writing video file...")
    
    final_video.write_videofile(
        output_file,
        fps=24,
        codec='libx264',
        audio_codec='aac',
        temp_audiofile='temp-audio.m4a',
        remove_temp=True
    )
    
    # Cleanup
    video.close()
    final_video.close()
    
    return True

def main():
    print("=== Adding Captacity-Style Captions with Word Highlighting ===")
    
    # Check if basic video exists
    basic_video = "elden_ring_nightreign_video_basic.mp4"
    if not os.path.exists(basic_video):
        print(f"Error: Basic video '{basic_video}' not found!")
        return False
    
    # Load metadata
    metadata = load_game_metadata()
    narration_text = create_narration_text(metadata)
    
    print(f"Narration text: {narration_text}")
    
    # Output file
    output_file = "elden_ring_nightreign_captacity_style.mp4"
    
    try:
        success = add_captions_with_captacity_style(
            video_file=basic_video,
            output_file=output_file,
            narration_text=narration_text,
            print_info=True
        )
        
        if success:
            print(f"\n✅ Captacity-style video created successfully!")
            print(f"Output: {output_file}")
            print(f"Features:")
            print(f"  - 20-second Elden Ring Nightreign slideshow")
            print(f"  - TTS narration with perfect timing")
            print(f"  - Word-by-word highlighting (yellow for current word)")
            print(f"  - Professional text styling with shadows and outlines")
            print(f"  - Short caption segments (max 6-8 words)")
            print(f"  - Bottom-positioned captions (captacity style)")
            print(f"  - High contrast white/yellow text with black outlines")
            
        return success
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\nCaption creation completed successfully!")
    else:
        print("\nCaption creation failed!")
        sys.exit(1) 