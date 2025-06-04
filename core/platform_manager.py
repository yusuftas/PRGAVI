import os
import logging
import json
from typing import Optional, Dict, List
from datetime import datetime
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from config import config
from .models import Post, db_manager

logger = logging.getLogger(__name__)

class PlatformManager:
    """Manager for uploading content to social media platforms"""
    
    def __init__(self):
        self.youtube_credentials = None
        self.instagram_access_token = config.INSTAGRAM_ACCESS_TOKEN
        
    def upload_to_youtube(self, video_path: str, title: str, description: str, 
                         tags: List[str] = None) -> Optional[Dict]:
        """
        Upload video to YouTube Shorts
        
        Args:
            video_path: Path to the video file
            title: Video title
            description: Video description
            tags: List of tags for the video
            
        Returns:
            Dictionary with upload results
        """
        try:
            # Initialize YouTube API service
            youtube_service = self._get_youtube_service()
            if not youtube_service:
                return None
            
            # Prepare video metadata
            body = {
                'snippet': {
                    'title': title[:100],  # YouTube title limit
                    'description': description,
                    'tags': tags or [],
                    'categoryId': '20',  # Gaming category
                    'defaultLanguage': 'en',
                    'defaultAudioLanguage': 'en'
                },
                'status': {
                    'privacyStatus': 'public',  # Change to 'private' for testing
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Create media upload
            media = MediaFileUpload(
                video_path,
                chunksize=-1,
                resumable=True,
                mimetype='video/mp4'
            )
            
            # Execute upload
            logger.info(f"Starting YouTube upload for: {title}")
            
            request = youtube_service.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = request.execute()
            
            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            result = {
                'success': True,
                'platform_post_id': video_id,
                'url': video_url,
                'response': response
            }
            
            logger.info(f"YouTube upload successful: {video_url}")
            return result
            
        except HttpError as e:
            error_msg = f"YouTube API error: {e}"
            if e.resp.status == 403:
                error_msg += " - Check API quotas and permissions"
            elif e.resp.status == 401:
                error_msg += " - Authentication failed"
            
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
            
        except Exception as e:
            error_msg = f"YouTube upload failed: {e}"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
    
    def upload_to_instagram(self, video_path: str, caption: str) -> Optional[Dict]:
        """
        Upload video to Instagram Reels
        
        Args:
            video_path: Path to the video file
            caption: Caption for the post
            
        Returns:
            Dictionary with upload results
        """
        try:
            if not self.instagram_access_token:
                return {'success': False, 'error': 'Instagram access token not configured'}
            
            # Step 1: Create media container
            container_response = self._create_instagram_container(video_path, caption)
            if not container_response or not container_response.get('success'):
                return container_response
            
            container_id = container_response['container_id']
            
            # Step 2: Publish the media
            publish_response = self._publish_instagram_media(container_id)
            if not publish_response or not publish_response.get('success'):
                return publish_response
            
            result = {
                'success': True,
                'platform_post_id': publish_response['media_id'],
                'url': f"https://www.instagram.com/p/{publish_response['media_id']}/",
                'container_id': container_id
            }
            
            logger.info(f"Instagram upload successful: {result['url']}")
            return result
            
        except Exception as e:
            error_msg = f"Instagram upload failed: {e}"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
    
    def _get_youtube_service(self):
        """Get authenticated YouTube API service"""
        try:
            if not config.YOUTUBE_CLIENT_ID or not config.YOUTUBE_CLIENT_SECRET:
                logger.error("YouTube API credentials not configured")
                return None
            
            # For automated uploads, you'll need to implement OAuth flow
            # This is a simplified version - you'll need proper token management
            scopes = ['https://www.googleapis.com/auth/youtube.upload']
            
            # You would need to implement proper OAuth flow here
            # For now, returning None to indicate setup needed
            logger.warning("YouTube OAuth flow needs to be implemented")
            return None
            
        except Exception as e:
            logger.error(f"Error setting up YouTube service: {e}")
            return None
    
    def _create_instagram_container(self, video_path: str, caption: str) -> Dict:
        """Create Instagram media container"""
        try:
            # Instagram requires video to be publicly accessible
            # In production, you'd upload to a temporary public URL
            
            url = f"https://graph.facebook.com/v18.0/{config.INSTAGRAM_APP_ID}/media"
            
            data = {
                'media_type': 'REELS',
                'video_url': video_path,  # This needs to be a public URL
                'caption': caption,
                'access_token': self.instagram_access_token
            }
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            result = response.json()
            
            if 'id' in result:
                return {
                    'success': True,
                    'container_id': result['id']
                }
            else:
                return {
                    'success': False,
                    'error': f"Failed to create container: {result}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Error creating Instagram container: {e}"
            }
    
    def _publish_instagram_media(self, container_id: str) -> Dict:
        """Publish Instagram media from container"""
        try:
            url = f"https://graph.facebook.com/v18.0/{config.INSTAGRAM_APP_ID}/media_publish"
            
            data = {
                'creation_id': container_id,
                'access_token': self.instagram_access_token
            }
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            result = response.json()
            
            if 'id' in result:
                return {
                    'success': True,
                    'media_id': result['id']
                }
            else:
                return {
                    'success': False,
                    'error': f"Failed to publish media: {result}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Error publishing Instagram media: {e}"
            }
    
    def save_post_record(self, content_id: int, platform: str, 
                        upload_result: Dict) -> Optional[Post]:
        """Save post record to database"""
        try:
            with db_manager.get_session() as session:
                post = Post(
                    content_id=content_id,
                    platform=platform,
                    platform_post_id=upload_result.get('platform_post_id'),
                    posted_at=datetime.utcnow()
                )
                
                # Save initial metrics if available
                if 'response' in upload_result:
                    post.metrics_dict = {
                        'initial_response': upload_result['response'],
                        'upload_time': datetime.utcnow().isoformat()
                    }
                
                session.add(post)
                session.commit()
                session.refresh(post)
                
                logger.info(f"Saved post record: {platform} - {post.id}")
                return post
                
        except Exception as e:
            logger.error(f"Error saving post record: {e}")
            return None
    
    def get_platform_statistics(self, platform: str, days: int = 30) -> Dict:
        """Get posting statistics for a platform"""
        try:
            from datetime import timedelta
            from sqlalchemy import func
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            with db_manager.get_session() as session:
                posts = session.query(Post).filter(
                    Post.platform == platform,
                    Post.posted_at >= cutoff_date
                ).all()
                
                stats = {
                    'total_posts': len(posts),
                    'successful_posts': len([p for p in posts if p.platform_post_id]),
                    'failed_posts': len([p for p in posts if not p.platform_post_id]),
                    'recent_posts': []
                }
                
                # Add recent post details
                for post in posts[-10:]:  # Last 10 posts
                    stats['recent_posts'].append({
                        'id': post.id,
                        'posted_at': post.posted_at.isoformat(),
                        'platform_post_id': post.platform_post_id,
                        'success': bool(post.platform_post_id)
                    })
                
                return stats
                
        except Exception as e:
            logger.error(f"Error getting platform statistics: {e}")
            return {}
    
    def test_platform_connection(self, platform: str) -> Dict:
        """Test connection to a specific platform"""
        if platform.lower() == 'youtube':
            return self._test_youtube_connection()
        elif platform.lower() == 'instagram':
            return self._test_instagram_connection()
        else:
            return {'success': False, 'error': f'Unknown platform: {platform}'}
    
    def _test_youtube_connection(self) -> Dict:
        """Test YouTube API connection"""
        try:
            service = self._get_youtube_service()
            if not service:
                return {
                    'success': False,
                    'error': 'YouTube service not available - OAuth setup required'
                }
            
            # Test with a simple API call
            request = service.channels().list(part='snippet', mine=True)
            response = request.execute()
            
            return {
                'success': True,
                'message': 'YouTube API connection successful',
                'channel_count': len(response.get('items', []))
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'YouTube connection test failed: {e}'
            }
    
    def _test_instagram_connection(self) -> Dict:
        """Test Instagram API connection"""
        try:
            if not self.instagram_access_token:
                return {
                    'success': False,
                    'error': 'Instagram access token not configured'
                }
            
            # Test with a simple API call
            url = f"https://graph.facebook.com/v18.0/me"
            params = {'access_token': self.instagram_access_token}
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            result = response.json()
            
            return {
                'success': True,
                'message': 'Instagram API connection successful',
                'account_id': result.get('id', 'Unknown')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Instagram connection test failed: {e}'
            } 