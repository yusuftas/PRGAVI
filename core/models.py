from sqlalchemy import create_engine, Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json
from typing import List, Dict, Optional
from config import config

Base = declarative_base()

class Game(Base):
    """Game model representing Steam games"""
    __tablename__ = 'games'
    
    id = Column(Integer, primary_key=True)
    steam_id = Column(Integer, unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    developer = Column(String(255))
    price = Column(Float)
    rating_score = Column(Float)
    review_count = Column(Integer)
    release_date = Column(DateTime)
    genres = Column(Text)  # JSON string
    images = Column(Text)  # JSON string
    videos = Column(Text)  # JSON string
    last_updated = Column(DateTime, default=datetime.utcnow)
    used_in_content = Column(Boolean, default=False)
    
    # Relationships
    content = relationship("Content", back_populates="game")
    
    @property
    def genres_list(self) -> List[str]:
        """Get genres as a list"""
        if self.genres:
            try:
                return json.loads(self.genres)
            except json.JSONDecodeError:
                return []
        return []
    
    @genres_list.setter
    def genres_list(self, value: List[str]):
        """Set genres from a list"""
        self.genres = json.dumps(value)
    
    @property
    def images_list(self) -> List[str]:
        """Get images as a list"""
        if self.images:
            try:
                return json.loads(self.images)
            except json.JSONDecodeError:
                return []
        return []
    
    @images_list.setter
    def images_list(self, value: List[str]):
        """Set images from a list"""
        self.images = json.dumps(value)
    
    @property
    def videos_list(self) -> List[str]:
        """Get videos as a list"""
        if self.videos:
            try:
                return json.loads(self.videos)
            except json.JSONDecodeError:
                return []
        return []
    
    @videos_list.setter
    def videos_list(self, value: List[str]):
        """Set videos from a list"""
        self.videos = json.dumps(value)
    
    def __repr__(self):
        return f"<Game(id={self.id}, name='{self.name}', steam_id={self.steam_id})>"

class Content(Base):
    """Content model representing generated video content"""
    __tablename__ = 'content'
    
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'), nullable=False)
    original_description = Column(Text)
    ai_summary = Column(Text)
    script = Column(Text)
    voice_file_path = Column(String(500))
    video_file_path = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    game = relationship("Game", back_populates="content")
    posts = relationship("Post", back_populates="content")
    
    def __repr__(self):
        return f"<Content(id={self.id}, game_id={self.game_id}, created_at={self.created_at})>"

class Post(Base):
    """Post model representing social media posts"""
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True)
    content_id = Column(Integer, ForeignKey('content.id'), nullable=False)
    platform = Column(String(50), nullable=False)  # 'youtube', 'instagram', 'tiktok'
    platform_post_id = Column(String(255))
    posted_at = Column(DateTime, default=datetime.utcnow)
    performance_metrics = Column(Text)  # JSON string
    
    # Relationships
    content = relationship("Content", back_populates="posts")
    
    @property
    def metrics_dict(self) -> Dict:
        """Get performance metrics as a dictionary"""
        if self.performance_metrics:
            try:
                return json.loads(self.performance_metrics)
            except json.JSONDecodeError:
                return {}
        return {}
    
    @metrics_dict.setter
    def metrics_dict(self, value: Dict):
        """Set performance metrics from a dictionary"""
        self.performance_metrics = json.dumps(value)
    
    def __repr__(self):
        return f"<Post(id={self.id}, platform='{self.platform}', posted_at={self.posted_at})>"

class DatabaseManager:
    """Database manager for handling database operations"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or config.DATABASE_URL
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get a database session"""
        return self.SessionLocal()
    
    def init_db(self):
        """Initialize the database"""
        self.create_tables()
        print(f"Database initialized at: {self.database_url}")

# Global database manager instance
db_manager = DatabaseManager() 