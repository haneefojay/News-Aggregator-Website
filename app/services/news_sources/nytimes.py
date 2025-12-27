import httpx
from typing import List, Optional, Dict
from datetime import datetime
from .base import NewsSourceBase, ArticleData

class NYTimesSource(NewsSourceBase):
    BASE_URL = "https://api.nytimes.com/svc/search/v2"
    
    @property
    def rate_limit_delay(self) -> float:
        return 10.0  # NYT has very strict rate limits
    
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
            if response.status_code == 429:
                print(f"NYT Rate Limit Hit. Waiting...")
                return []
            response.raise_for_status()
            data = response.json()
            
        response_data = data.get("response")
        if not response_data:
            return []
            
        docs = response_data.get("docs", [])
        
        return [
            self._transform_article(doc) 
            for doc in docs
            if isinstance(doc, dict)
        ]
    
    def _transform_article(self, raw: Dict) -> ArticleData:
        headline = raw.get("headline", {})
        multimedia = raw.get("multimedia", [])
        image_url = None
        
        # Safely get a high-quality image URL
        if multimedia and isinstance(multimedia, list) and len(multimedia) > 0:
            # Try to find a high-quality format (e.g., 'xlarge' or 'superJumbo')
            best_image = multimedia[0]
            for m in multimedia:
                if isinstance(m, dict) and m.get("subtype") == "xlarge":
                    best_image = m
                    break
            
            if isinstance(best_image, dict) and "url" in best_image:
                image_url = f"https://www.nytimes.com/{best_image['url']}"
            
        return ArticleData(
            title=headline.get("main", "No Title"),
            description=raw.get("abstract") or raw.get("snippet"),
            content=raw.get("lead_paragraph"),
            url=raw.get("web_url", ""),
            source="NYTimes",
            author=raw.get("byline", {}).get("original"),
            category=raw.get("section_name"),
            published_at=datetime.fromisoformat(
                raw.get("pub_date", datetime.utcnow().isoformat()).replace("Z", "+00:00")
            ),
            image_url=image_url,
            raw_data=raw
        )
