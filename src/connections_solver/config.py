"""Application configuration using Pydantic Settings."""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        environment: Environment name (development, production, etc.)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        cors_origins: Comma-separated list of allowed CORS origins
        storage_type: Type of storage to use ("memory" or "sqlite")
        database_path: Path to SQLite database file (only used if storage_type is "sqlite")
    """

    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000,http://localhost:8000"
    storage_type: str = "memory"
    database_path: str = "data/connections.db"

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        case_sensitive = False

    def get_cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into a list.

        Returns:
            List of CORS origin URLs
        """
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()
