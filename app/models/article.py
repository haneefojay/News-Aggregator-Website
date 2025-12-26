from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.core.database import Base

class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Core fields
    title = Column(String(500), nullable=False)
    description = Column(Text)
    content = Column(Text)
    url = Column(String(2000), unique=True, nullable=False)
    url_hash = Column(String(64), unique=True, index=True)
    
    # Metadata
    source = Column(String(100), nullable=False, index=True)
    author = Column(String(500))
    category = Column(String(100), index=True)
    published_at = Column(DateTime(timezone=True), index=True)
    
    # Images
    image_url = Column(String(2000))
    
    # Intelligence Layer
    read_time_minutes = Column(Integer, default=1)
    sentiment = Column(String(20), default="neutral") # positive, neutral, urgent
    
    # Raw data
    raw_data = Column(JSONB)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Composite indices for common queries
    __table_args__ = (
        Index('idx_source_published', 'source', 'published_at'),
        Index('idx_category_published', 'category', 'published_at'),
        # Note: GIN index for search requires PostgreSQL and pg_trgm extension
        # We'll define it but it might need manual setup in DB for some environments
        Index('idx_article_search', 
              'title', 'description', 
              postgresql_using='gin',
              postgresql_ops={'title': 'gin_trgm_ops', 'description': 'gin_trgm_ops'}),
    )
