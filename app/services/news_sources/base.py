from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

class ArticleData(BaseModel):
    """Standardized article format from any source"""
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    url: str
    source: str
    author: Optional[str] = None
    category: Optional[str] = None
    published_at: datetime
    image_url: Optional[str] = None
    raw_data: Dict[str, Any]

class NewsSourceBase(ABC):
    """Abstract base class for all news sources"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.source_name = self.__class__.__name__
    
    @abstractmethod
    async def fetch_articles(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        from_date: Optional[datetime] = None,
        page_size: int = 100
    ) -> List[ArticleData]:
        """
        Fetch articles from the news source.
        
        Returns standardized ArticleData objects.
        """
        pass
    
    @abstractmethod
    def _transform_article(self, raw_article: Dict) -> ArticleData:
        """
        Transform source-specific article format to standardized ArticleData.
        """
        pass
    
    @property
    @abstractmethod
    def rate_limit_delay(self) -> float:
        """Seconds to wait between requests (respect API limits)"""
        pass
