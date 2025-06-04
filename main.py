#!/usr/bin/env python3
"""
GameVids Automation - Main Application
Automated gaming content creation and social media posting
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from typing import List, Dict
import schedule
import time

from config import config
from core import SteamScraper, AIContentProcessor, VideoGenerator, PlatformManager
from core.models import Game, Content, Post, db_manager

# Set up logging
def setup_logging():
    """Configure logging for the application"""
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    
    log_filename = os.path.join(log_dir, f"gamesvids_{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(sys.stdout)
        ]
    )

logger = logging.getLogger(__name__)

class GameVidsAutomation:
    """Main automation class for GameVids content creation"""
    
    def __init__(self):
        self.steam_scraper = SteamScraper()
        self.ai_processor = AIContentProcessor()
        self.video_generator = VideoGenerator()
        self.platform_manager = PlatformManager()
        
        # Ensure database is initialized
        db_manager.init_db()
        
        logger.info("GameVids Automation initialized")
    
    def create_daily_content(self, game_count: int = None) -> List[Dict]:
        """
        Create daily gaming content
        
        Args:
            game_count: Number of games to create content for
            
        Returns:
            List of created content results
        """
        game_count = game_count or config.DAILY_VIDEO_COUNT
        results = []
        
        logger.info(f"Starting daily content creation for {game_count} games")
        
        try:
            # Step 1: Get random popular games
            games = self.steam_scraper.get_random_popular_games(
                count=game_count,
                min_reviews=config.MIN_GAME_REVIEWS
            )
            
            if not games:
                logger.error("No suitable games found for content creation")
                return results
            
            # Step 2: Process each game
            for game in games:
                try:
                    result = self._process_single_game(game)
                    results.append(result)
                    
                    # Mark game as used if successful
                    if result.get('success'):
                        self.steam_scraper.mark_game_as_used(game.id)
                    
                    # Add delay between games to be respectful
                    time.sleep(2)
                    
                except Exception as e:
                    error_result = {
                        'success': False,
                        'game_name': game.name,
                        'error': str(e)
                    }
                    results.append(error_result)
                    logger.error(f"Error processing game {game.name}: {e}")
            
            logger.info(f"Daily content creation completed. {len([r for r in results if r.get('success')])} successful, {len([r for r in results if not r.get('success')])} failed")
            return results
            
        except Exception as e:
            logger.error(f"Error in daily content creation: {e}")
            return results
    
    def _process_single_game(self, game: Game) -> Dict:
        """Process a single game to create content"""
        logger.info(f"Processing game: {game.name}")
        
        try:
            # Step 1: Create AI summary and script
            script = self.ai_processor.summarize_for_short(
                game.description,
                max_words=80
            )
            
            if not script:
                return {
                    'success': False,
                    'game_name': game.name,
                    'error': 'Failed to generate script'
                }
            
            # Step 2: Generate voiceover
            voiceover_path = self.ai_processor.generate_voiceover(script)
            
            if not voiceover_path:
                return {
                    'success': False,
                    'game_name': game.name,
                    'error': 'Failed to generate voiceover'
                }
            
            # Step 3: Create video
            game_data = {
                'name': game.name,
                'developer': game.developer,
                'rating_score': game.rating_score,
                'images': game.images_list
            }
            
            video_path = self.video_generator.create_video(
                game_data=game_data,
                script=script,
                voiceover_path=voiceover_path
            )
            
            if not video_path:
                return {
                    'success': False,
                    'game_name': game.name,
                    'error': 'Failed to create video'
                }
            
            # Step 4: Save content record
            content_record = self._save_content_record(
                game=game,
                script=script,
                voiceover_path=voiceover_path,
                video_path=video_path
            )
            
            if not content_record:
                return {
                    'success': False,
                    'game_name': game.name,
                    'error': 'Failed to save content record'
                }
            
            # Step 5: Upload to platforms (optional for now)
            upload_results = {}
            if config.DEBUG:
                logger.info("Debug mode: Skipping platform uploads")
            else:
                upload_results = self._upload_to_platforms(
                    content_record, video_path, game, script
                )
            
            return {
                'success': True,
                'game_name': game.name,
                'content_id': content_record.id,
                'video_path': video_path,
                'script': script,
                'upload_results': upload_results
            }
            
        except Exception as e:
            logger.error(f"Error processing game {game.name}: {e}")
            return {
                'success': False,
                'game_name': game.name,
                'error': str(e)
            }
    
    def _save_content_record(self, game: Game, script: str, voiceover_path: str, 
                           video_path: str) -> Content:
        """Save content creation record to database"""
        try:
            with db_manager.get_session() as session:
                content = Content(
                    game_id=game.id,
                    original_description=game.description,
                    ai_summary=script,
                    script=script,
                    voice_file_path=voiceover_path,
                    video_file_path=video_path
                )
                
                session.add(content)
                session.commit()
                session.refresh(content)
                
                logger.info(f"Saved content record: {content.id}")
                return content
                
        except Exception as e:
            logger.error(f"Error saving content record: {e}")
            return None
    
    def _upload_to_platforms(self, content: Content, video_path: str, 
                           game: Game, script: str) -> Dict:
        """Upload content to social media platforms"""
        results = {}
        
        # Prepare upload metadata
        title = f"🎮 {game.name} - Game Recommendation"
        description = f"{script}\n\n#gaming #shorts #gamedev #indie"
        tags = ['gaming', 'gamedev', 'indie', 'shorts']
        
        # Add genre tags if available
        if game.genres_list:
            tags.extend(game.genres_list[:3])  # Add up to 3 genre tags
        
        try:
            # Upload to YouTube
            youtube_result = self.platform_manager.upload_to_youtube(
                video_path=video_path,
                title=title,
                description=description,
                tags=tags
            )
            
            if youtube_result and youtube_result.get('success'):
                # Save post record
                self.platform_manager.save_post_record(
                    content.id, 'youtube', youtube_result
                )
                results['youtube'] = youtube_result
                logger.info("YouTube upload successful")
            else:
                results['youtube'] = youtube_result or {'success': False, 'error': 'Unknown error'}
                logger.warning("YouTube upload failed")
            
            # Upload to Instagram
            instagram_caption = f"{script}\n\n#gaming #reels #gamedev"
            instagram_result = self.platform_manager.upload_to_instagram(
                video_path=video_path,
                caption=instagram_caption
            )
            
            if instagram_result and instagram_result.get('success'):
                # Save post record
                self.platform_manager.save_post_record(
                    content.id, 'instagram', instagram_result
                )
                results['instagram'] = instagram_result
                logger.info("Instagram upload successful")
            else:
                results['instagram'] = instagram_result or {'success': False, 'error': 'Unknown error'}
                logger.warning("Instagram upload failed")
                
        except Exception as e:
            logger.error(f"Error uploading to platforms: {e}")
            results['error'] = str(e)
        
        return results
    
    def test_components(self) -> Dict:
        """Test all system components"""
        results = {}
        
        logger.info("Testing system components...")
        
        # Test Steam scraper
        try:
            featured_games = self.steam_scraper.get_featured_games()
            results['steam_scraper'] = {
                'success': len(featured_games) > 0,
                'games_found': len(featured_games)
            }
        except Exception as e:
            results['steam_scraper'] = {'success': False, 'error': str(e)}
        
        # Test AI processor
        try:
            voice_info = self.ai_processor.get_voice_info()
            results['ai_processor'] = {
                'success': voice_info.get('total_voices', 0) > 0,
                'voices_available': voice_info.get('total_voices', 0)
            }
        except Exception as e:
            results['ai_processor'] = {'success': False, 'error': str(e)}
        
        # Test platform connections
        try:
            youtube_test = self.platform_manager.test_platform_connection('youtube')
            instagram_test = self.platform_manager.test_platform_connection('instagram')
            
            results['platforms'] = {
                'youtube': youtube_test,
                'instagram': instagram_test
            }
        except Exception as e:
            results['platforms'] = {'success': False, 'error': str(e)}
        
        return results
    
    def schedule_daily_automation(self):
        """Set up scheduled daily content creation"""
        schedule_time = f"{config.UPLOAD_SCHEDULE_HOUR:02d}:{config.UPLOAD_SCHEDULE_MINUTE:02d}"
        
        schedule.every().day.at(schedule_time).do(self.create_daily_content)
        
        logger.info(f"Scheduled daily content creation at {schedule_time}")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description='GameVids Automation')
    parser.add_argument('--mode', choices=['once', 'schedule', 'test'], 
                       default='once', help='Run mode')
    parser.add_argument('--count', type=int, default=None,
                       help='Number of videos to create (overrides config)')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    
    logger.info("Starting GameVids Automation")
    logger.info(f"Mode: {args.mode}")
    
    # Validate configuration
    if not config.validate_required_keys():
        logger.error("Missing required API keys. Please check your .env file")
        sys.exit(1)
    
    # Create directories
    config.create_directories()
    
    # Initialize automation
    automation = GameVidsAutomation()
    
    if args.mode == 'test':
        # Test mode - check all components
        results = automation.test_components()
        print("\n" + "="*50)
        print("COMPONENT TEST RESULTS")
        print("="*50)
        for component, result in results.items():
            status = "✅ PASS" if result.get('success') else "❌ FAIL"
            print(f"{status} {component}")
            if not result.get('success') and 'error' in result:
                print(f"    Error: {result['error']}")
        
    elif args.mode == 'once':
        # Run once mode
        results = automation.create_daily_content(game_count=args.count)
        
        print("\n" + "="*50)
        print("CONTENT CREATION RESULTS")
        print("="*50)
        
        successful = [r for r in results if r.get('success')]
        failed = [r for r in results if not r.get('success')]
        
        print(f"✅ Successful: {len(successful)}")
        print(f"❌ Failed: {len(failed)}")
        
        for result in successful:
            print(f"  ✅ {result['game_name']} -> {result['video_path']}")
        
        for result in failed:
            print(f"  ❌ {result['game_name']} -> {result.get('error', 'Unknown error')}")
    
    elif args.mode == 'schedule':
        # Scheduled mode
        logger.info("Starting scheduled automation...")
        try:
            automation.schedule_daily_automation()
        except KeyboardInterrupt:
            logger.info("Scheduled automation stopped by user")

if __name__ == "__main__":
    main() 