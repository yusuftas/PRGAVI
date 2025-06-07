#!/usr/bin/env python3
"""
Video End Trimmer

This script cuts a specified number of seconds from the end of a video file.

Usage:
    python trim_video_end.py input_video.mp4 5 output_video.mp4
    
Arguments:
    input_file: Path to the input video file
    seconds_to_cut: Number of seconds to cut from the end
    output_file: Path to save the trimmed video (optional, defaults to input_trimmed.ext)
"""

import sys
import os
from pathlib import Path
from moviepy.editor import VideoFileClip


def trim_video_end(input_file, seconds_to_cut, output_file=None):
    """
    Trim specified seconds from the end of a video file.
    
    Args:
        input_file (str): Path to input video file
        seconds_to_cut (float): Number of seconds to cut from the end
        output_file (str, optional): Path to output file. If None, auto-generates name.
    
    Returns:
        str: Path to the output file
    """
    # Validate input file exists
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    # Generate output filename if not provided
    if output_file is None:
        input_path = Path(input_file)
        output_file = input_path.parent / f"{input_path.stem}_trimmed{input_path.suffix}"
    
    print(f"Loading video: {input_file}")
    
    # Load the video
    video = VideoFileClip(input_file)
    
    # Get video duration
    original_duration = video.duration
    print(f"Original duration: {original_duration:.2f} seconds")
    
    # Calculate new duration
    new_duration = original_duration - seconds_to_cut
    
    if new_duration <= 0:
        raise ValueError(f"Cannot cut {seconds_to_cut} seconds from a {original_duration:.2f} second video")
    
    print(f"Cutting {seconds_to_cut} seconds from the end")
    print(f"New duration: {new_duration:.2f} seconds")
    
    # Trim the video (keep from start to new_duration)
    # Using subclip method which should properly handle both video and audio
    trimmed_video = video.subclip(0, new_duration)
    
    print(f"Writing trimmed video to: {output_file}")
    
    # Write the trimmed video with explicit parameters
    trimmed_video.write_videofile(
        str(output_file),
        fps=video.fps,
        codec='libx264',
        audio_codec='aac',
        temp_audiofile='temp-audio.m4a',
        remove_temp=True,
        verbose=True,
        logger=None
    )
    
    # Clean up
    video.close()
    trimmed_video.close()
    
    # Verify the output file
    print("Verifying output file...")
    verification_video = VideoFileClip(str(output_file))
    actual_duration = verification_video.duration
    verification_video.close()
    
    print(f"Verification: Output video duration is {actual_duration:.2f} seconds")
    
    if abs(actual_duration - new_duration) > 0.1:  # Allow small tolerance
        print(f"WARNING: Expected {new_duration:.2f}s but got {actual_duration:.2f}s")
    else:
        print("✓ Duration verification passed")
    
    print(f"Successfully trimmed video saved to: {output_file}")
    return str(output_file)


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 3:
        print("Usage: python trim_video_end.py <input_file> <seconds_to_cut> [output_file]")
        print("\nExample: python trim_video_end.py video.mp4 5")
        print("Example: python trim_video_end.py video.mp4 5 trimmed_video.mp4")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        seconds_to_cut = float(sys.argv[2])
    except ValueError:
        print("Error: seconds_to_cut must be a number")
        sys.exit(1)
    
    if seconds_to_cut < 0:
        print("Error: seconds_to_cut must be positive")
        sys.exit(1)
    
    output_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    try:
        result_file = trim_video_end(input_file, seconds_to_cut, output_file)
        print(f"\n✓ Video trimming completed successfully!")
        print(f"Output file: {result_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 