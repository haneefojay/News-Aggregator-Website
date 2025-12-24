import asyncio
from datetime import datetime, timedelta, timezone
from typing import List

from app.tasks import celery_app
from app.core.database import AsyncSessionLocal
from app.services.article_service import ArticleService
from app.services.news_sources.newsapi import NewsAPISource
from app.services.news_sources.guardian import GuardianSource
from app.services.news_sources.nytimes import NYTimesSource
from app.config import get_settings
from app.core.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

@celery_app.task(name="fetch_all_sources", bind=True, max_retries=3)
def fetch_all_sources(self):
    """
    Celery task to fetch articles from all configured sources.
    """
    try:
        # Run async code in sync Celery task
        return asyncio.run(_fetch_all_sources_async())
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

async def _fetch_all_sources_async():
    """Actual async fetching logic"""
    from app.core.database import create_db_engine, AsyncSession, async_sessionmaker
    
    # Create a task-specific engine to avoid "Event loop is closed" errors
    task_engine = create_db_engine(settings.DATABASE_URL, pool_size=2, max_overflow=0)
    TaskSessionLocal = async_sessionmaker(task_engine, class_=AsyncSession, expire_on_commit=False)
    
    # Initialize sources
    sources = []
    if settings.NEWSAPI_KEY:
        sources.append(NewsAPISource(settings.NEWSAPI_KEY))
    if settings.GUARDIAN_API_KEY:
        sources.append(GuardianSource(settings.GUARDIAN_API_KEY))
    if settings.NYTIMES_API_KEY:
        sources.append(NYTimesSource(settings.NYTIMES_API_KEY))
    
    if not sources:
        print("No news API keys configured. Skipping fetch.")
        await task_engine.dispose()
        return "No sources configured"
    
    # Fetch from last 24 hours
    from_date = datetime.now(timezone.utc) - timedelta(days=1)
    
    results = {}
    
    async with TaskSessionLocal() as db:
        article_service = ArticleService(db)
        
        for source in sources:
            try:
                print(f"Fetching from {source.source_name}...")
                
                articles = await source.fetch_articles(
                    from_date=from_date,
                    page_size=50
                )
                
                new_count = 0
                for article_data in articles:
                    try:
                        article = await article_service.create_article(article_data)
                        if article:
                            new_count += 1
                    except Exception as e:
                        print(f"Skipping article due to error: {e}")
                        continue
                
                await db.commit()
                results[source.source_name] = new_count
                print(f"Added {new_count} new articles from {source.source_name}")
                
                # Respect rate limits
                await asyncio.sleep(source.rate_limit_delay)
                
            except Exception as e:
                print(f"Error fetching from {source.source_name}: {e}")
                await db.rollback()
                results[source.source_name] = f"Error: {str(e)}"
                continue
    
    # Crucial: Close everything
    await task_engine.dispose()
                
    return results
