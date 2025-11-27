"""Tests for settings configuration."""

import pytest

from apisbot.config.settings import Settings, get_settings


class TestSettings:
    """Test Settings configuration."""

    def test_settings_from_env(self, monkeypatch):
        """Test loading settings from environment variables."""
        monkeypatch.setenv("BOT_TOKEN", "test_token_123")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("SESSION_TIMEOUT", "3600")

        # Clear the lru_cache to force reload
        get_settings.cache_clear()

        settings = Settings()

        assert settings.bot_token == "test_token_123"
        assert settings.log_level == "DEBUG"
        assert settings.session_timeout == 3600

    def test_settings_defaults(self, monkeypatch):
        """Test default values for optional settings."""
        monkeypatch.setenv("BOT_TOKEN", "test_token")
        # Don't set optional variables

        settings = Settings()

        assert settings.bot_token == "test_token"
        assert settings.log_level == "INFO"  # Default
        assert settings.session_timeout == 1800  # Default (30 minutes)

    def test_settings_case_insensitive(self, monkeypatch):
        """Test that settings are case-insensitive."""
        monkeypatch.setenv("bot_token", "lowercase_token")
        monkeypatch.setenv("LOG_LEVEL", "warning")

        settings = Settings()

        assert settings.bot_token == "lowercase_token"
        assert settings.log_level == "warning"

    def test_settings_missing_required(self):
        """Test that settings requires bot_token."""
        # Settings requires bot_token, verify it's in the model
        from pydantic import ValidationError as PydanticValidationError
        from pydantic_core import ValidationError

        # Try creating Settings without bot_token (will fail)
        with pytest.raises((ValidationError, PydanticValidationError)):
            Settings(_env_file=None)  # Force no env file to ensure missing token

    def test_settings_extra_fields_ignored(self, monkeypatch):
        """Test that extra environment variables are ignored."""
        monkeypatch.setenv("BOT_TOKEN", "test_token")
        monkeypatch.setenv("EXTRA_FIELD", "should_be_ignored")
        monkeypatch.setenv("ANOTHER_VAR", "also_ignored")

        settings = Settings()

        assert settings.bot_token == "test_token"
        assert not hasattr(settings, "extra_field")
        assert not hasattr(settings, "another_var")

    def test_get_settings_cached(self, monkeypatch):
        """Test that get_settings returns cached instance."""
        monkeypatch.setenv("BOT_TOKEN", "cached_token")

        # Clear cache first
        get_settings.cache_clear()

        settings1 = get_settings()
        settings2 = get_settings()

        # Should be the same instance due to lru_cache
        assert settings1 is settings2
        assert settings1.bot_token == "cached_token"

    def test_settings_timeout_as_string(self, monkeypatch):
        """Test that session_timeout can be provided as string."""
        monkeypatch.setenv("BOT_TOKEN", "test_token")
        monkeypatch.setenv("SESSION_TIMEOUT", "7200")

        settings = Settings()

        assert settings.session_timeout == 7200
        assert isinstance(settings.session_timeout, int)

    def test_settings_validation(self, monkeypatch):
        """Test settings validation with various inputs."""
        monkeypatch.setenv("BOT_TOKEN", "valid_token")

        # Valid settings
        settings = Settings()
        assert settings.bot_token == "valid_token"

        # Test with different log levels
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            monkeypatch.setenv("LOG_LEVEL", level)
            get_settings.cache_clear()
            settings = Settings()
            assert settings.log_level == level
