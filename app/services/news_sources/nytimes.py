import httpx
from typing import List, Optional, Dict
from datetime import datetime
from .base import NewsSourceBase, ArticleData

class NYTimesSource(NewsSourceBase):
    BASE_URL = "https://api.nytimes.com/svc/search/v2"
    
    @property
    def rate_limit_delay(self) -> float:
        return 6.0  # NYT has strict rate limits (default 5-10 requests per minute)
    
    async def fetch_articles(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        from_date: Optional[datetime] = None,
        page_size: int = 10  # NYT returns 10 per page
    ) -> List[ArticleData]:
        
        params = {
            "api-key": self.api_key,
        }
        
        if query:
            params["q"] = query
            
        if category:
            params["fq"] = f'section_name:("{category}")'
            
        if from_date:
            params["begin_date"] = from_date.strftime("%Y%m%d")
            
        endpoint = f"{self.BASE_URL}/articlesearch.json"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            
        docs = data.get("response", {}).get("docs", [])
        
        return [
            self._transform_article(doc) 
            for doc in docs
        ]
    
    def _transform_article(self, raw: Dict) -> ArticleData:
        headline = raw.get("headline", {})
        multimedia = raw.get("multimedia", [])
        image_url = None
        if multimedia:
            # Find the largest image or just use the first one
            image_url = f"https://www.nytimes.com/{multimedia[0]['url']}"
            
        return ArticleData(
            title=headline.get("main", "No Title"),
            description=raw.get("abstract") or raw.get("snippet"),
            content=raw.get("lead_paragraph"),
            url=raw["web_url"],
            source="NYTimes",
            author=raw.get("byline", {}).get("original"),
            category=raw.get("section_name"),
            published_at=datetime.fromisoformat(
                raw["pub_date"].replace("Z", "+00:00")
            ),
            image_url=image_url,
            raw_data=raw
        )
