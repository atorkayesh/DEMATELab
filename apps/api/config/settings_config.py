"""
Application settings loaded from environment variables.

Values come from the process environment, falling back to `apps/api/.env` for local runs.
Docker Compose sets them directly.
"""

from functools import lru_cache
from typing import List, Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Validated application settings.

    Attributes:
        app_env: Runtime environment (`development` or `production`)
        cors_origins: Comma-separated list of allowed CORS origins
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: Literal["development", "production"] = "development"
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        """
        Parse `cors_origins` into a list.

        Returns:
            List[str]: Non-empty, trimmed origins
        """
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """
    Return the cached application settings.

    Returns:
        Settings: Settings parsed once per process
    """
    return Settings()
