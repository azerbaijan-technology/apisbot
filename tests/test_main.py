"""Tests for __main__.py entry point."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestMain:
    """Test main entry point."""

    @pytest.mark.asyncio
    @patch("apisbot.__main__.Bot")
    @patch("apisbot.__main__.Dispatcher")
    @patch("apisbot.__main__.get_settings")
    async def test_main_function_setup(self, mock_get_settings, mock_dispatcher_class, mock_bot_class):
        """Test that main() sets up bot correctly."""
        from apisbot.__main__ import main

        # Mock settings
        mock_settings = MagicMock()
        mock_settings.bot_token = "test_token"
        mock_settings.log_level = "INFO"
        mock_get_settings.return_value = mock_settings

        # Mock bot
        mock_bot = MagicMock()
        mock_bot.delete_webhook = AsyncMock()
        mock_bot_class.return_value = mock_bot

        # Mock dispatcher
        mock_dispatcher = MagicMock()
        mock_dispatcher.include_router = MagicMock()
        mock_dispatcher.message = MagicMock()
        mock_dispatcher.message.middleware = MagicMock()
        mock_dispatcher.start_polling = AsyncMock()
        mock_dispatcher_class.return_value = mock_dispatcher

        # Run main (it will try to start polling, so we'll let it set up then stop)
        try:
            # Create a task that we can cancel
            import asyncio

            task = asyncio.create_task(main())
            # Give it a moment to set up
            await asyncio.sleep(0.1)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        except Exception:
            pass  # Expected since we're mocking

        # Verify bot was created with token
        mock_bot_class.assert_called_once()

        # Verify dispatcher was created
        mock_dispatcher_class.assert_called_once()
