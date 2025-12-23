import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.database import Base
from app.services.article_service import ArticleService
from app.services.news_sources.base import ArticleData
from datetime import datetime

# Setup test DB (using SQLite for simplicity in unit tests if needed, 
# but for asyncpg we might need a real test Postgres or mock)
# For now, let's mock the session for service tests.

@pytest.fixture
def mock_db_session(mocker):
    return mocker.AsyncMock(spec=AsyncSession)

@pytest.mark.asyncio
async def test_article_service_create(mock_db_session):
    # Mocking select result
    from sqlalchemy.engine import Result
    mock_result = mocker.Mock(spec=Result)
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result
    
    service = ArticleService(mock_db_session)
    
    article_data = ArticleData(
        title="Test Article",
        description="Test Description",
        content="Test Content",
        url="https://example.com/test",
        source="Test Source",
        published_at=datetime.utcnow(),
        raw_data={}
    )
    
    article = await service.create_article(article_data)
    
    assert article is not None
    assert article.title == "Test Article"
    mock_db_session.add.assert_called_once()
