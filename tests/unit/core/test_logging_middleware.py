"""Tests for logging middleware."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import CallbackQuery, Chat, Message, Update, User

from apisbot.bot.middlewares.logging_middleware import LoggingMiddleware


class TestLoggingMiddleware:
    """Test LoggingMiddleware."""

    @pytest.mark.asyncio
    async def test_middleware_logs_message(self):
        """Test that middleware logs regular messages."""
        middleware = LoggingMiddleware()
        handler = AsyncMock()

        user = User(id=123, is_bot=False, first_name="Test")
        chat = Chat(id=456, type="private")
        message = Message(message_id=1, date=0, chat=chat, from_user=user, text="Hello")
        update = Update(update_id=1, message=message)

        with patch("apisbot.bot.middlewares.logging_middleware.logger") as mock_logger:
            await middleware(handler, update, {})

            mock_logger.info.assert_called()
            call_args = str(mock_logger.info.call_args)
            assert "123" in call_args
            assert "message" in call_args

    @pytest.mark.asyncio
    async def test_middleware_logs_command(self):
        """Test that middleware logs commands."""
        middleware = LoggingMiddleware()
        handler = AsyncMock()

        user = User(id=456, is_bot=False, first_name="Test")
        chat = Chat(id=789, type="private")
        message = Message(message_id=1, date=0, chat=chat, from_user=user, text="/start")
        update = Update(update_id=1, message=message)

        with patch("apisbot.bot.middlewares.logging_middleware.logger") as mock_logger:
            await middleware(handler, update, {})

            mock_logger.info.assert_called()
            call_args = str(mock_logger.info.call_args)
            assert "456" in call_args
            assert "command" in call_args

    @pytest.mark.asyncio
    async def test_middleware_logs_callback_query(self):
        """Test that middleware logs callback queries."""
        middleware = LoggingMiddleware()
        handler = AsyncMock()

        user = User(id=789, is_bot=False, first_name="Test")
        callback = CallbackQuery(id="test", from_user=user, chat_instance="instance", data="callback_data")
        update = Update(update_id=1, callback_query=callback)

        with patch("apisbot.bot.middlewares.logging_middleware.logger") as mock_logger:
            await middleware(handler, update, {})

            mock_logger.info.assert_called()
            call_args = str(mock_logger.info.call_args)
            assert "789" in call_args
            assert "callback" in call_args

    @pytest.mark.asyncio
    async def test_middleware_calls_handler(self):
        """Test that middleware calls the handler."""
        middleware = LoggingMiddleware()
        handler = AsyncMock(return_value="result")

        user = User(id=123, is_bot=False, first_name="Test")
        chat = Chat(id=456, type="private")
        message = Message(message_id=1, date=0, chat=chat, from_user=user, text="Hello")
        update = Update(update_id=1, message=message)
        data = {"key": "value"}

        result = await middleware(handler, update, data)

        handler.assert_called_once_with(update, data)
        assert result == "result"

    @pytest.mark.asyncio
    async def test_middleware_logs_errors(self):
        """Test that middleware logs errors from handlers."""
        middleware = LoggingMiddleware()
        handler = AsyncMock(side_effect=ValueError("Test error"))

        user = User(id=123, is_bot=False, first_name="Test")
        chat = Chat(id=456, type="private")
        message = Message(message_id=1, date=0, chat=chat, from_user=user, text="Hello")
        update = Update(update_id=1, message=message)

        with patch("apisbot.bot.middlewares.logging_middleware.logger") as mock_logger:
            with pytest.raises(ValueError, match="Test error"):
                await middleware(handler, update, {})

            # Check that error was logged
            mock_logger.error.assert_called()
            call_args = str(mock_logger.error.call_args)
            assert "ValueError" in call_args
            assert "Test error" in call_args

    @pytest.mark.asyncio
    async def test_middleware_handles_message_without_user(self):
        """Test middleware handling message without user info."""
        middleware = LoggingMiddleware()
        handler = AsyncMock()

        chat = Chat(id=456, type="private")
        message = Message(message_id=1, date=0, chat=chat, text="Hello")
        update = Update(update_id=1, message=message)

        with patch("apisbot.bot.middlewares.logging_middleware.logger") as mock_logger:
            await middleware(handler, update, {})

            mock_logger.info.assert_called()
            call_args = str(mock_logger.info.call_args)
            assert "None" in call_args

    @pytest.mark.asyncio
    async def test_middleware_handles_non_update_event(self):
        """Test middleware with non-Update event."""
        middleware = LoggingMiddleware()
        handler = AsyncMock(return_value="result")

        event = MagicMock()  # Some other TelegramObject
        data = {}

        result = await middleware(handler, event, data)

        # Should still call handler even if not an Update
        handler.assert_called_once_with(event, data)
        assert result == "result"
