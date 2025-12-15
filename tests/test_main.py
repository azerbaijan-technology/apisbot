"""Tests for __main__.py entry point."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestMain:
    """Test main entry point."""

    @pytest.mark.asyncio
    @patch("apisbot.__main__.setup_dialogs")
    @patch("apisbot.__main__.get_birth_data_dialog")
    @patch("apisbot.__main__.set_start_commands")
    @patch("apisbot.__main__.MemoryStorage")
    @patch("apisbot.__main__.Bot")
    @patch("apisbot.__main__.Dispatcher")
    @patch("apisbot.__main__.get_settings")
    async def test_main_function_setup(
        self,
        mock_get_settings,
        mock_dispatcher_class,
        mock_bot_class,
        mock_memory_storage_class,
        mock_set_start_commands,
        mock_get_birth_data_dialog,
        mock_setup_dialogs,
    ):
        """Test that main() sets up bot correctly."""
        from apisbot.__main__ import main

        # Mock settings
        mock_settings = MagicMock()
        mock_settings.bot_token = "test_token"
        mock_settings.log_level = "INFO"
        mock_settings.session_timeout = 300
        mock_get_settings.return_value = mock_settings

        # Mock storage
        mock_storage = MagicMock()
        mock_memory_storage_class.return_value = mock_storage

        # Mock bot
        mock_bot = MagicMock()
        mock_bot.delete_webhook = AsyncMock()
        mock_bot.session = MagicMock()
        mock_bot.session.close = AsyncMock()
        mock_bot_class.return_value = mock_bot

        # Mock set_start_commands
        mock_set_start_commands.return_value = AsyncMock()()

        # Mock dispatcher
        mock_dispatcher = MagicMock()
        mock_dispatcher.include_router = MagicMock()
        mock_dispatcher.update = MagicMock()
        mock_dispatcher.update.middleware = MagicMock()
        mock_dispatcher.resolve_used_update_types = MagicMock(return_value=[])
        mock_dispatcher.start_polling = AsyncMock()
        mock_dispatcher_class.return_value = mock_dispatcher

        # Mock dialog
        mock_dialog = MagicMock()
        mock_get_birth_data_dialog.return_value = mock_dialog

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
        call_kwargs = mock_bot_class.call_args.kwargs
        assert call_kwargs["token"] == "test_token"

        # Verify storage was created
        mock_memory_storage_class.assert_called_once()

        # Verify dispatcher was created with storage
        mock_dispatcher_class.assert_called_once_with(storage=mock_storage)

        # Verify routers were included
        assert mock_dispatcher.include_router.call_count >= 3
