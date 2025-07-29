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
    allowed_origins_env: str = Field("*", env="ALLOWED_ORIGINS")

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

    @property
    def allowed_origins(self) -> List[str]:
        if self.allowed_origins_env.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.allowed_origins_env.split(",") if o.strip()]

@lru_cache()
def get_settings() -> Settings:
    return Settings()