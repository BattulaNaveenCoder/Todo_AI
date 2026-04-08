import logging

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application configuration loaded from environment variables.

    Raises:
        ValidationError: If required environment variables are missing.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    DATABASE_URL: str
    CORS_ORIGINS: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse comma-separated CORS_ORIGINS into a list.

        Returns:
            List of allowed origin strings.
        """
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()  # type: ignore[call-arg] — fields populated from .env at runtime
