from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
from math import ceil

from app.core.database import get_db
from app.core.cache import CacheManager, get_cache
from app.services.article_service import ArticleService
from app.schemas.article import ArticleResponse, PaginatedArticles

router = APIRouter()

@router.get("/articles", response_model=PaginatedArticles)
async def search_articles(
    query: Optional[str] = Query(None, description="Search query"),
    source: Optional[str] = Query(None, description="Filter by source"),
    category: Optional[str] = Query(None, description="Filter by category"),
    from_date: Optional[datetime] = Query(None, description="Start date"),
    to_date: Optional[datetime] = Query(None, description="End date"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    cache: CacheManager = Depends(get_cache)
):
    """
    Search and filter articles with caching.
    """
    # Create cache key
    cache_params = f"{query}:{source}:{category}:{from_date}:{to_date}:{page}:{page_size}"
    cache_key = f"articles:search:{hash(cache_params)}"
    
    # Try cache
    cached = await cache.get(cache_key)
    if cached:
        return PaginatedArticles(**cached)
    
    service = ArticleService(db)
    skip = (page - 1) * page_size
    
    articles, total = await service.search_articles(
        query=query,
        source=source,
        category=category,
        from_date=from_date,
        to_date=to_date,
        skip=skip,
        limit=page_size
    )
    
    response_data = PaginatedArticles(
        articles=[ArticleResponse.from_orm(a) for a in articles],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size) if total > 0 else 0
    )
    
    # Set cache (limit to 5 mins for search results)
    await cache.set(cache_key, response_data.model_dump(), ttl=300)
    
    return response_data

@router.get("/articles/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a single article by ID"""
    from sqlalchemy import select
    from app.models.article import Article
    
    result = await db.execute(
        select(Article).where(Article.id == article_id)
    )
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return ArticleResponse.from_orm(article)
