from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # App
    APP_NAME: str = "News Aggregator API"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str
    CACHE_TTL: int = 3600  # 1 hour
    
    # News APIs
    NEWSAPI_KEY: str = ""
    GUARDIAN_API_KEY: str = ""
    NYTIMES_API_KEY: str = ""
    
    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    FETCH_INTERVAL_MINUTES: int = 240
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    from pydantic import field_validator

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_db_url(cls, v: str) -> str:
        if not v or not isinstance(v, str):
            return v
        
        # Handle 'postgres://' which is common on platforms like Railway
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql://", 1)
            
        # Ensure we're using the asyncpg driver
        if v.startswith("postgresql://") and "+asyncpg" not in v:
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
            
        return v

    @field_validator("REDIS_URL", "CELERY_BROKER_URL", "CELERY_RESULT_BACKEND")
    @classmethod
    def validate_redis_url(cls, v: str) -> str:
        if not v.startswith("redis://"):
            raise ValueError("Redis URLs must start with 'redis://'")
        return v
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        case_sensitive=True,
        extra="ignore" # Ignore extra env vars
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()
