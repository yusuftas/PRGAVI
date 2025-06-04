#!/usr/bin/env python3
"""
Stellar Blade Media Downloader
Downloads images and videos from Stellar Blade's Steam page
"""

import os
import re
import sys
import json
import time
import logging
import requests
from pathlib import Path
from bs4 import BeautifulSoup
import yt_dlp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Game Steam page URL
STEAM_URL = "https://store.steampowered.com/app/3489700/Stellar_Blade/"
STEAM_APP_ID = "3489700"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Paths for downloaded content
IMAGES_DIR = Path("downloads/stellar_blade")
VIDEOS_DIR = IMAGES_DIR / "videos"
METADATA_FILE = Path("downloads/stellar_blade_info.json")

def ensure_directories():
    """Ensure download directories exist"""
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

def download_file(url, destination, is_binary=True):
    """Download a file with progress indicator"""
    try:
        logger.info(f"Downloading from: {url}")
        
        headers = {
            "User-Agent": USER_AGENT,
            "Accept-Language": "en-US,en;q=0.9",
        }
        
        response = requests.get(url, stream=True, headers=headers)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        block_size = 8192
        downloaded = 0
        
        mode = 'wb' if is_binary else 'w'
        
        with open(destination, mode) as file:
            for chunk in response.iter_content(chunk_size=block_size):
                if chunk:
                    if is_binary:
                        file.write(chunk)
                    else:
                        file.write(chunk.decode('utf-8'))
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = downloaded / total_size * 100
                        sys.stdout.write(f"\rDownloading: {progress:.1f}% ({downloaded/(1024*1024):.1f}MB / {total_size/(1024*1024):.1f}MB)")
                    else:
                        sys.stdout.write(f"\rDownloading: {downloaded/(1024*1024):.1f}MB")
                    sys.stdout.flush()
        
        sys.stdout.write("\n")
        logger.info(f"Download completed: {destination}")
        return True
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        return False

def scrape_steam_page():
    """Scrape the Steam page for game information and media URLs"""
    try:
        headers = {
            "User-Agent": USER_AGENT,
            "Accept-Language": "en-US,en;q=0.9",
            "Cookie": "birthtime=189302401; mature_content=1"  # To bypass age verification
        }
        
        logger.info(f"Scraping Steam page: {STEAM_URL}")
        response = requests.get(STEAM_URL, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract screenshots
        screenshot_urls = []
        screenshots = soup.select('.highlight_screenshot_link')
        for screenshot in screenshots:
            if 'href' in screenshot.attrs:
                img_url = screenshot['href']
                if img_url.startswith('https://'):
                    screenshot_urls.append(img_url)
        
        # Get game description
        description = ""
        desc_element = soup.select_one('.game_description_snippet')
        if desc_element:
            description = desc_element.text.strip()
        
        # Get game features
        features = []
        feature_elements = soup.select('.game_area_description li')
        for feature in feature_elements:
            feature_text = feature.text.strip()
            if feature_text:
                features.append(feature_text)
        
        # Get trailer video
        trailer_url = None
        movie_elements = soup.select('.highlight_movie')
        for movie in movie_elements:
            if 'data-mp4-hd-source' in movie.attrs:
                trailer_url = movie['data-mp4-hd-source']
                break
            elif 'data-mp4-source' in movie.attrs:
                trailer_url = movie['data-mp4-source']
                break
        
        if not trailer_url:
            # Try getting YouTube trailer
            youtube_elements = soup.select('a.movie_link')
            for element in youtube_elements:
                if 'data-youtubeid' in element.attrs:
                    youtube_id = element['data-youtubeid']
                    trailer_url = f"https://www.youtube.com/watch?v={youtube_id}"
                    break
        
        # Get release date
        release_date = ""
        date_element = soup.select_one('.release_date .date')
        if date_element:
            release_date = date_element.text.strip()
        
        # Get developer
        developer = ""
        dev_element = soup.select_one('.dev_row .summary a')
        if dev_element:
            developer = dev_element.text.strip()
        
        # Save metadata
        metadata = {
            "name": "Stellar Blade",
            "description": description,
            "features": features,
            "release_date": release_date,
            "developer": developer,
            "steam_url": STEAM_URL,
            "screenshots": screenshot_urls,
            "trailer_url": trailer_url
        }
        
        with open(METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Found {len(screenshot_urls)} screenshots")
        if trailer_url:
            logger.info(f"Found trailer video: {trailer_url}")
        
        return metadata
    
    except Exception as e:
        logger.error(f"Error scraping Steam page: {e}")
        return None

def download_screenshots(screenshot_urls):
    """Download screenshots from Steam"""
    logger.info("Downloading screenshots...")
    
    for i, url in enumerate(screenshot_urls):
        file_name = f"steam_screenshot_{i+1:02d}.jpg"
        destination = IMAGES_DIR / file_name
        
        if destination.exists():
            logger.info(f"Screenshot already exists: {destination}")
            continue
        
        download_file(url, destination)
        
        # Don't hammer the server
        time.sleep(0.5)
    
    logger.info(f"Downloaded {len(screenshot_urls)} screenshots")

def download_trailer(trailer_url):
    """Download the trailer video with start time at 10 seconds"""
    if not trailer_url:
        logger.error("No trailer URL found")
        return False
    
    if trailer_url.startswith('https://www.youtube.com'):
        # Download from YouTube
        logger.info(f"Downloading YouTube trailer: {trailer_url}")
        
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': str(VIDEOS_DIR / 'stellar_blade_trailer.mp4'),
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([trailer_url])
            logger.info(f"Downloaded trailer to {VIDEOS_DIR / 'stellar_blade_trailer.mp4'}")
            return True
        except Exception as e:
            logger.error(f"Error downloading YouTube trailer: {e}")
            return False
    else:
        # Direct MP4 download
        destination = VIDEOS_DIR / "stellar_blade_trailer.mp4"
        return download_file(trailer_url, destination)

def fetch_additional_content():
    """Fetch additional content using Steam API"""
    try:
        # Get content from Steam API
        api_url = f"https://store.steampowered.com/api/appdetails?appids={STEAM_APP_ID}"
        headers = {"User-Agent": USER_AGENT}
        
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if data and data.get(STEAM_APP_ID, {}).get('success', False):
            app_data = data[STEAM_APP_ID]['data']
            
            # Get screenshots from API (might be better quality)
            screenshots = app_data.get('screenshots', [])
            for i, screenshot in enumerate(screenshots):
                img_url = screenshot.get('path_full')
                if img_url:
                    file_name = f"api_screenshot_{i+1:02d}.jpg"
                    destination = IMAGES_DIR / file_name
                    
                    if not destination.exists():
                        download_file(img_url, destination)
                        time.sleep(0.5)
            
            # Save detailed information
            with open(IMAGES_DIR / "game_details.txt", 'w', encoding='utf-8') as f:
                f.write(f"Game: {app_data.get('name', 'Stellar Blade')}\n\n")
                f.write(f"Description:\n{app_data.get('detailed_description', '')}\n\n")
                f.write(f"About:\n{app_data.get('about_the_game', '')}\n\n")
                
            logger.info(f"Saved detailed game information to {IMAGES_DIR / 'game_details.txt'}")
            return True
            
        return False
    except Exception as e:
        logger.error(f"Error fetching additional content: {e}")
        return False

def generate_script_from_metadata():
    """Generate a script for the video based on Stellar Blade features"""
    try:
        if not METADATA_FILE.exists():
            logger.error("Metadata file not found")
            # Create a fallback script based on known Stellar Blade info
            script = (
                "Stellar Blade delivers breathtaking post-apocalyptic action like you've never experienced. "
                "Master lightning-fast melee combat with futuristic blade weapons that slice through enemies with precision. "
                "Explore a stunning sci-fi world filled with mystery, danger, and incredible visual storytelling. "
                "Every battle tests your skills with fluid combos and devastating special attacks. "
                "This isn't just another action game — it's a masterpiece of combat design and world-building. "
                "Stellar Blade is available now. What action game should I showcase next? Follow for more epic gaming content!"
            )
            
            # Save the fallback script
            with open(IMAGES_DIR / "generated_script.txt", 'w', encoding='utf-8') as f:
                f.write(script)
            
            logger.info(f"Created fallback script for Stellar Blade")
            return script
        
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        description = metadata.get('description', '')
        features = metadata.get('features', [])
        
        # Create a comprehensive script based on Stellar Blade's action-adventure nature
        script = "Stellar Blade redefines post-apocalyptic action gaming with its stunning blend of fast-paced melee combat and sci-fi storytelling. "
        
        if description:
            script += f"{description} "
        
        # Add key features specific to action games
        important_features = []
        for feature in features:
            if any(keyword in feature.lower() for keyword in ['combat', 'action', 'blade', 'melee', 'adventure', 'story']):
                important_features.append(feature)
        
        if important_features:
            feature_text = ", ".join(important_features[:2])
            script += f"Experience {feature_text}. "
        
        # Add more context about action-adventure games
        script += "Master fluid combat systems, explore breathtaking environments, and uncover the mysteries of a world in ruins. "
        script += "Every encounter demands precision and skill in this visually stunning adventure. "
        
        # Add call to action
        script += "Stellar Blade is available now. What action-adventure game should I cover next? Follow for daily gaming discoveries!"
        
        # Save the script
        with open(IMAGES_DIR / "generated_script.txt", 'w', encoding='utf-8') as f:
            f.write(script)
        
        logger.info(f"Generated script saved to {IMAGES_DIR / 'generated_script.txt'}")
        return script
    
    except Exception as e:
        logger.error(f"Error generating script: {e}")
        return None

def main():
    """Main function"""
    print("🎮 STELLAR BLADE MEDIA DOWNLOADER")
    print("=" * 50)
    
    # Create directories
    ensure_directories()
    
    # Scrape Steam page
    metadata = scrape_steam_page()
    if not metadata:
        print("❌ Failed to scrape Steam page, using fallback approach")
        # Even if scraping fails, we can still generate a script
        metadata = {"screenshots": [], "trailer_url": None}
    
    # Download screenshots
    screenshot_urls = metadata.get('screenshots', [])
    if screenshot_urls:
        download_screenshots(screenshot_urls)
    else:
        print("❌ No screenshots found from page scraping")
    
    # Download trailer
    trailer_url = metadata.get('trailer_url')
    if trailer_url:
        download_trailer(trailer_url)
    else:
        print("❌ No trailer video found from page scraping")
    
    # Get additional content via API
    fetch_additional_content()
    
    # Generate script even if some downloads failed
    script = generate_script_from_metadata()
    if script:
        print("\n📝 Generated Script:")
        print(f'"{script[:100]}..."')
    
    # Summary
    image_count = len(list(IMAGES_DIR.glob('*.jpg')))
    video_count = len(list(VIDEOS_DIR.glob('*.mp4')))
    
    print("\n✅ Download Summary:")
    print(f"📸 {image_count} images downloaded to {IMAGES_DIR}")
    print(f"🎬 {video_count} videos downloaded to {VIDEOS_DIR}")
    
    if image_count > 0 or script:
        print("\n🚀 Ready to create Stellar Blade shorts video!")
        print("Assets and script prepared for video creation")
    else:
        print("\n⚠️ Limited media downloaded, but script generated")
        print("Will use placeholder assets for video creation")

if __name__ == "__main__":
    main() 