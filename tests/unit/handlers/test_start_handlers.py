"""Tests for start command handlers."""

from unittest.mock import AsyncMock

import pytest

from apisbot.bot.handlers.start import cmd_cancel, cmd_help, cmd_start


class TestStartHandler:
    """Test /start command handler."""

    @pytest.mark.asyncio
    async def test_cmd_start(self, mock_message, mock_state):
        """Test /start command."""
        await cmd_start(mock_message, mock_state)

        mock_state.clear.assert_called_once()
        mock_message.answer.assert_called_once()

        # Check welcome message content
        call_args = mock_message.answer.call_args[0][0]
        assert "Welcome" in call_args
        assert "chart" in call_args.lower()

        # Start command should set state to ChartSelection
        mock_state.set_state.assert_called_once()


class TestHelpHandler:
    """Test /help command handler."""

    @pytest.mark.asyncio
    async def test_cmd_help(self, mock_message):
        """Test /help command."""
        await cmd_help(mock_message)

        mock_message.answer.assert_called_once()

        # Check help message content
        call_args = mock_message.answer.call_args[0][0]
        assert "/start" in call_args
        assert "/help" in call_args
        assert "/cancel" in call_args
        assert "Date formats" in call_args or "date format" in call_args.lower()
        assert "Time formats" in call_args or "time format" in call_args.lower()


class TestCancelHandler:
    """Test /cancel command handler."""

    @pytest.mark.asyncio
    async def test_cmd_cancel_with_active_state(self, mock_message, mock_state):
        """Test /cancel with an active state."""
        mock_state.get_state = AsyncMock(return_value="SomeState:some_state")

        await cmd_cancel(mock_message, mock_state)

        mock_state.get_state.assert_called_once()
        mock_state.clear.assert_called_once()
        mock_message.answer.assert_called_once()

        # Check cancellation message
        call_args = mock_message.answer.call_args[0][0]
        assert "cancel" in call_args.lower() or "cleared" in call_args.lower()

    @pytest.mark.asyncio
    async def test_cmd_cancel_without_active_state(self, mock_message, mock_state):
        """Test /cancel without an active state."""
        mock_state.get_state = AsyncMock(return_value=None)

        await cmd_cancel(mock_message, mock_state)

        mock_state.get_state.assert_called_once()
        mock_state.clear.assert_not_called()
        mock_message.answer.assert_called_once()

        # Check message indicates nothing to cancel
        call_args = mock_message.answer.call_args[0][0]
        assert "nothing" in call_args.lower() or "no" in call_args.lower()
