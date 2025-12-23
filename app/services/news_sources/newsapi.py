import httpx
from typing import List, Optional, Dict
from datetime import datetime
from .base import NewsSourceBase, ArticleData

class NewsAPISource(NewsSourceBase):
    BASE_URL = "https://newsapi.org/v2"
    
    @property
    def rate_limit_delay(self) -> float:
        return 1.0  # 1 request per second
    
    async def fetch_articles(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        from_date: Optional[datetime] = None,
        page_size: int = 100
    ) -> List[ArticleData]:
        
        params = {
            "apiKey": self.api_key,
            "pageSize": min(page_size, 100),
            "language": "en",
        }
        
        if query:
            params["q"] = query
            endpoint = f"{self.BASE_URL}/everything"
        else:
            endpoint = f"{self.BASE_URL}/top-headlines"
            if category:
                params["category"] = category
        
        if from_date:
            params["from"] = from_date.isoformat()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()
        
        return [
            self._transform_article(article) 
            for article in data.get("articles", [])
        ]
    
    def _transform_article(self, raw: Dict) -> ArticleData:
        return ArticleData(
            title=raw["title"],
            description=raw.get("description"),
            content=raw.get("content"),
            url=raw["url"],
            source="NewsAPI",
            author=raw.get("author"),
            category=None,
            published_at=datetime.fromisoformat(
                raw["publishedAt"].replace("Z", "+00:00")
            ),
            image_url=raw.get("urlToImage"),
            raw_data=raw
        )
