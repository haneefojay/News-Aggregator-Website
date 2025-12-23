from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional, List

class ArticleBase(BaseModel):
    title: str
    description: Optional[str] = None
    url: str
    source: str

class ArticleCreate(ArticleBase):
    content: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    published_at: datetime
    image_url: Optional[str] = None
    raw_data: Optional[dict] = None

class ArticleResponse(ArticleBase):
    id: int
    content: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    published_at: datetime
    image_url: Optional[str] = None
    
    class Config:
        from_attributes = True

class PaginatedArticles(BaseModel):
    articles: List[ArticleResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
