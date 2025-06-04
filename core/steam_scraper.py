import requests
import time
import random
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from datetime import datetime
import logging
from config import config
from .models import Game, db_manager

logger = logging.getLogger(__name__)

class SteamScraper:
    """Steam scraper for fetching game data"""
    
    def __init__(self):
        self.api_key = config.STEAM_API_KEY
        self.base_url = "https://api.steampowered.com"
        self.store_url = "https://store.steampowered.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def get_featured_games(self) -> List[Dict]:
        """Get featured games from Steam"""
        try:
            url = f"{self.store_url}/api/featured/"
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            featured_games = []
            
            # Extract from different featured sections
            sections = ['large_capsules', 'featured_win', 'featured_mac', 'featured_linux']
            
            for section in sections:
                if section in data:
                    items = data[section] if isinstance(data[section], list) else [data[section]]
                    for item in items:
                        if isinstance(item, dict) and 'id' in item:
                            featured_games.append({
                                'steam_id': item['id'],
                                'name': item.get('name', ''),
                                'discount_percent': item.get('discount_percent', 0)
                            })
            
            logger.info(f"Found {len(featured_games)} featured games")
            return featured_games
            
        except Exception as e:
            logger.error(f"Error fetching featured games: {e}")
            return []
    
    def get_app_details(self, app_id: int) -> Optional[Dict]:
        """Get detailed app information from Steam API"""
        try:
            url = f"{self.store_url}/api/appdetails"
            params = {
                'appids': app_id,
                'format': 'json'
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            app_data = data.get(str(app_id))
            
            if not app_data or not app_data.get('success'):
                return None
                
            game_data = app_data.get('data', {})
            
            # Extract relevant information
            details = {
                'steam_id': app_id,
                'name': game_data.get('name', ''),
                'description': game_data.get('detailed_description', ''),
                'short_description': game_data.get('short_description', ''),
                'developer': ', '.join(game_data.get('developers', [])),
                'price': self._extract_price(game_data.get('price_overview', {})),
                'genres': [genre['description'] for genre in game_data.get('genres', [])],
                'release_date': game_data.get('release_date', {}).get('date', ''),
                'images': self._extract_images(game_data),
                'videos': self._extract_videos(game_data)
            }
            
            return details
            
        except Exception as e:
            logger.error(f"Error fetching app details for {app_id}: {e}")
            return None
    
    def _extract_price(self, price_overview: Dict) -> float:
        """Extract price from price overview"""
        if not price_overview:
            return 0.0
        
        # Convert from cents to dollars
        final_price = price_overview.get('final', 0)
        return final_price / 100.0 if final_price else 0.0
    
    def _extract_images(self, game_data: Dict) -> List[str]:
        """Extract screenshot URLs from game data"""
        images = []
        
        # Screenshots
        screenshots = game_data.get('screenshots', [])
        for screenshot in screenshots:
            if 'path_full' in screenshot:
                images.append(screenshot['path_full'])
        
        # Header image
        if 'header_image' in game_data:
            images.insert(0, game_data['header_image'])
            
        return images
    
    def _extract_videos(self, game_data: Dict) -> List[str]:
        """Extract video URLs from game data"""
        videos = []
        
        movie_data = game_data.get('movies', [])
        for movie in movie_data:
            if 'mp4' in movie and 'max' in movie['mp4']:
                videos.append(movie['mp4']['max'])
                
        return videos
    
    def get_user_reviews(self, app_id: int, num_reviews: int = 100) -> Dict:
        """Get user reviews for a game"""
        try:
            url = f"{self.store_url}/appreviews/{app_id}"
            params = {
                'json': 1,
                'filter': 'recent',
                'language': 'english',
                'num_per_page': min(num_reviews, 100)
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('success') != 1:
                return {}
            
            query_summary = data.get('query_summary', {})
            
            return {
                'total_reviews': query_summary.get('total_reviews', 0),
                'total_positive': query_summary.get('total_positive', 0),
                'total_negative': query_summary.get('total_negative', 0),
                'review_score': query_summary.get('review_score', 0),
                'review_score_desc': query_summary.get('review_score_desc', '')
            }
            
        except Exception as e:
            logger.error(f"Error fetching reviews for {app_id}: {e}")
            return {}
    
    def get_trending_games(self, min_reviews: int = None, limit: int = 50) -> List[Game]:
        """Get trending games with minimum review count"""
        min_reviews = min_reviews or config.MIN_GAME_REVIEWS
        games = []
        
        try:
            # Get featured games as starting point
            featured_games = self.get_featured_games()
            
            for featured_game in featured_games[:limit]:
                app_id = featured_game['steam_id']
                
                # Get detailed app information
                app_details = self.get_app_details(app_id)
                if not app_details:
                    continue
                
                # Get reviews information
                reviews = self.get_user_reviews(app_id)
                total_positive = reviews.get('total_positive', 0)
                
                # Filter by review count
                if total_positive < min_reviews:
                    continue
                
                # Calculate rating score (0-100)
                total_reviews = reviews.get('total_reviews', 0)
                rating_score = (total_positive / total_reviews * 100) if total_reviews > 0 else 0
                
                # Create Game object
                game = Game(
                    steam_id=app_details['steam_id'],
                    name=app_details['name'],
                    description=app_details['description'],
                    developer=app_details['developer'],
                    price=app_details['price'],
                    rating_score=rating_score,
                    review_count=total_positive,
                    genres=app_details['genres'],
                    images=app_details['images'],
                    videos=app_details['videos']
                )
                
                games.append(game)
                
                # Add delay to be respectful
                time.sleep(random.uniform(1, 2))
                
                logger.info(f"Added game: {app_details['name']} (Reviews: {total_positive})")
        
        except Exception as e:
            logger.error(f"Error getting trending games: {e}")
        
        logger.info(f"Found {len(games)} games meeting criteria")
        return games
    
    def get_random_popular_games(self, count: int = 2, min_reviews: int = None) -> List[Game]:
        """Get random popular games for content creation"""
        min_reviews = min_reviews or config.MIN_GAME_REVIEWS
        
        # Check if we have unused games in database first
        with db_manager.get_session() as session:
            unused_games = session.query(Game).filter(
                Game.used_in_content == False,
                Game.review_count >= min_reviews
            ).all()
            
            if len(unused_games) >= count:
                selected_games = random.sample(unused_games, count)
                logger.info(f"Selected {count} unused games from database")
                return selected_games
        
        # If not enough unused games, fetch new ones
        trending_games = self.get_trending_games(min_reviews, limit=100)
        
        if len(trending_games) < count:
            logger.warning(f"Only found {len(trending_games)} games, requested {count}")
            return trending_games
        
        selected_games = random.sample(trending_games, count)
        
        # Save new games to database
        with db_manager.get_session() as session:
            for game in selected_games:
                existing_game = session.query(Game).filter(Game.steam_id == game.steam_id).first()
                if not existing_game:
                    session.add(game)
            session.commit()
        
        logger.info(f"Selected {count} new games and saved to database")
        return selected_games
    
    def mark_game_as_used(self, game_id: int):
        """Mark a game as used in content creation"""
        with db_manager.get_session() as session:
            game = session.query(Game).filter(Game.id == game_id).first()
            if game:
                game.used_in_content = True
                session.commit()
                logger.info(f"Marked game {game.name} as used") 