from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from sqlalchemy.sql import func
from typing import List, Optional, Tuple
from datetime import datetime
import hashlib

from app.models.article import Article
from app.services.news_sources.base import ArticleData
from app.services.intelligence_service import IntelligenceService

class ArticleService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @staticmethod
    def generate_url_hash(url: str) -> str:
        """Generate SHA256 hash of URL for duplicate detection"""
        return hashlib.sha256(url.encode()).hexdigest()
    
    async def create_article(self, article_data: ArticleData) -> Optional[Article]:
        """
        Create article if it doesn't exist.
        Returns None if duplicate.
        """
        url_hash = self.generate_url_hash(article_data.url)
        
        # Check if exists
        result = await self.db.execute(
            select(Article).where(Article.url_hash == url_hash)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            return None
        
        # Intelligence calculations
        read_time = IntelligenceService.calculate_read_time(
            f"{article_data.description} {article_data.content}"
        )
        # Create new article
        article = Article(
            title=article_data.title,
            description=article_data.description,
            content=article_data.content,
            url=article_data.url,
            url_hash=url_hash,
            source=article_data.source,
            author=article_data.author,
            category=article_data.category,
            published_at=article_data.published_at,
            image_url=article_data.image_url,
            raw_data=article_data.raw_data,
            read_time_minutes=read_time
        )
        
        self.db.add(article)
        await self.db.flush()
        return article
    
    async def search_articles(
        self,
        query: Optional[str] = None,
        source: Optional[str] = None,
        category: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Article], int]:
        """
        Search articles with filters.
        """
        conditions = []
        
        if query:
            search_condition = or_(
                Article.title.ilike(f"%{query}%"),
                Article.description.ilike(f"%{query}%")
            )
            conditions.append(search_condition)
        
        if source:
            conditions.append(Article.source == source)
        
        if category:
            cat_lower = category.lower()
            if cat_lower == "sports":
                conditions.append(or_(
                    Article.category.ilike("sports"),
                    Article.category.ilike("sport"),
                    Article.category.ilike("football"),
                    Article.category.ilike("soccer"),
                    Article.category.ilike("tennis"),
                    Article.category.ilike("basketball")
                ))
            elif cat_lower == "politics":
                conditions.append(or_(
                    Article.category.ilike("politics"),
                    Article.category.ilike("uk news"),
                    Article.category.ilike("us news"),
                    Article.category.ilike("world news"),
                    Article.category.ilike("society")
                ))
            elif cat_lower == "technology":
                conditions.append(or_(
                    Article.category.ilike("technology"),
                    Article.category.ilike("tech")
                ))
            else:
                conditions.append(Article.category.ilike(category))
        
        if from_date:
            conditions.append(Article.published_at >= from_date)
        
        if to_date:
            conditions.append(Article.published_at <= to_date)
        
        # Count total
        count_query = select(func.count()).select_from(Article)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Get paginated
        articles_query = select(Article)
        if conditions:
            articles_query = articles_query.where(and_(*conditions))
        
        articles_query = (
            articles_query
            .order_by(Article.published_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.db.execute(articles_query)
        articles = result.scalars().all()
        
        # Diagnostic Log
        if articles:
            sources_found = set(a.source for a in articles)
            categories_found = set(a.category for a in articles)
            print(f"DEBUG SEARCH: Found {len(articles)} articles. Sources: {sources_found}, Categories: {categories_found}")
        
        return list(articles), total
