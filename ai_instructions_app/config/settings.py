"""Application settings and configuration helpers."""
from __future__ import annotations

from functools import lru_cache
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application configuration leveraging environment variables."""

    flask_env: str = Field(default="development", alias="FLASK_ENV")
    secret_key: str = Field(default="dev-secret", alias="SECRET_KEY")
    database_url: str = Field(default="sqlite:///./instance/app.db", alias="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_endpoint: str | None = Field(default=None, alias="OPENAI_ENDPOINT")
    langfuse_public_key: str | None = Field(default=None, alias="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: str | None = Field(default=None, alias="LANGFUSE_SECRET_KEY")
    max_file_size: int = Field(default=50 * 1024 * 1024, alias="MAX_FILE_SIZE")
    max_concurrent_workflows: int = Field(default=10, alias="MAX_CONCURRENT_WORKFLOWS")
    workflow_timeout: int = Field(default=3600, alias="WORKFLOW_TIMEOUT")

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        populate_by_name=True,
    )

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:  # pragma: no cover - compatibility helper
        """Provide compatibility with Flask-SQLAlchemy expected config."""
        return self.database_url


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
