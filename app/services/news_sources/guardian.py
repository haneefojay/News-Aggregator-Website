import httpx
from typing import List, Optional, Dict
from datetime import datetime, timezone
from .base import NewsSourceBase, ArticleData

class GuardianSource(NewsSourceBase):
    BASE_URL = "https://content.guardianapis.com"
    
    @property
    def rate_limit_delay(self) -> float:
        return 0.5  # 2 requests per second
    
    async def fetch_articles(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        from_date: Optional[datetime] = None,
        page_size: int = 50
    ) -> List[ArticleData]:
        
        params = {
            "api-key": self.api_key,
            "page-size": min(page_size, 50),
            "show-fields": "all",
        }
        
        if query:
            params["q"] = query
        
        if category:
            # Guardian section for Sports is "sport"
            section = "sport" if category.lower() == "sports" else category
            params["section"] = section
            
        if from_date:
            params["from-date"] = from_date.strftime("%Y-%m-%d")
            
        endpoint = f"{self.BASE_URL}/search"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            
        results = data.get("response", {}).get("results", [])
        
        return [
            self._transform_article(article) 
            for article in results
        ]
    
    def _transform_article(self, raw: Dict) -> ArticleData:
        fields = raw.get("fields", {})
        
        # Require title and URL
        title = raw.get("webTitle")
        url = raw.get("webUrl")
        
        if not title or not url:
            raise ValueError("Missing title or URL in Guardian article")

        return ArticleData(
            title=title,
            description=fields.get("trailText"),
            content=fields.get("body"),
            url=url,
            source="Guardian",
            author=fields.get("byline"),
            category=raw.get("sectionName"),
            published_at=datetime.fromisoformat(
                raw.get("webPublicationDate", datetime.now(timezone.utc).isoformat()).replace("Z", "+00:00")
            ),
            image_url=fields.get("thumbnail"),
            raw_data=raw
        )
