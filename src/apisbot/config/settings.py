from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables.

    Attributes:
        bot_token: Telegram bot token from @BotFather
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        session_timeout: Session timeout in seconds (default: 30 minutes)
    """

    bot_token: str
    log_level: str = "INFO"
    session_timeout: int = 1800  # 30 minutes in seconds

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields from environment
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()  # type: ignore[call-arg]
