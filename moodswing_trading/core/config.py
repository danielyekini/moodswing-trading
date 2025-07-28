from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    database_url: str = Field("sqlite:///./moodswing.db", env="DATABASE_URL")
    redis_url: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    # broker_url: str = Field(None, env="BROKER_URL")
    # result_backend: str = Field(None, env="RESULT_BACKEND")
    tickers_env: str = Field("", env="TICKERS")

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def celery_broker(self) -> str:
        return self.broker_url or self.redis_url

    @property
    def celery_backend(self) -> str:
        return self.result_backend or self.redis_url

    @property
    def tickers(self) -> List[str]:
        return [t.strip().upper() for t in self.tickers_env.split(",") if t.strip()]

@lru_cache()
def get_settings() -> Settings:
    return Settings()