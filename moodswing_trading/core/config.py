from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",
        case_sensitive=False,
        extra="ignore",
    )

    # App environment: development, staging, production
    environment: str = Field("development", alias="ENVIRONMENT")
    # Database connection string. Defaults to local SQLite for dev.
    database_url: str = Field("sqlite:///./moodswing.db", alias="DATABASE_URL")
    redis_url: str = Field("redis://localhost:6379/0", alias="REDIS_URL")
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    broker_url: str | None = Field(None, alias="BROKER_URL")
    result_backend: str | None = Field(None, alias="RESULT_BACKEND")
    tickers_env: str = Field("", alias="TICKERS")
    allowed_origins_env: str = Field("*", alias="ALLOWED_ORIGINS")

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
    settings = Settings()
    # Normalize blank/whitespace DATABASE_URL to the dev default
    if not (settings.database_url or "").strip():
        settings.database_url = "sqlite:///./moodswing.db"
    # Enforce Postgres in production to avoid accidental SQLite usage
    if settings.environment.lower() in {"prod", "production"}:
        if settings.database_url.startswith("sqlite"):
            raise ValueError(
                "DATABASE_URL must be set to a Postgres URL in production. "
                "Set ENVIRONMENT=production and provide DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/dbname"
            )
    return settings