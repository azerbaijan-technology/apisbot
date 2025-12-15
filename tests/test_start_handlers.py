"""Tests for start command handlers."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, User

from apisbot.bot.handlers.start import cmd_cancel, cmd_help, cmd_start


class TestStartHandler:
    """Test /start command handler."""

    @pytest.mark.asyncio
    async def test_cmd_start(self):
        """Test /start command."""
        message = MagicMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.clear = AsyncMock()
        state.set_state = AsyncMock()

        await cmd_start(message, state)

        state.clear.assert_called_once()
        message.answer.assert_called_once()

        # Check welcome message content
        call_args = message.answer.call_args[0][0]
        assert "Welcome" in call_args
        assert "chart" in call_args.lower()

        # Start command should set state to ChartSelection
        state.set_state.assert_called_once()


class TestHelpHandler:
    """Test /help command handler."""

    @pytest.mark.asyncio
    async def test_cmd_help(self):
        """Test /help command."""
        message = MagicMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        await cmd_help(message)

        message.answer.assert_called_once()

        # Check help message content
        call_args = message.answer.call_args[0][0]
        assert "/start" in call_args
        assert "/help" in call_args
        assert "/cancel" in call_args
        assert "Date formats" in call_args or "date format" in call_args.lower()
        assert "Time formats" in call_args or "time format" in call_args.lower()


class TestCancelHandler:
    """Test /cancel command handler."""

    @pytest.mark.asyncio
    async def test_cmd_cancel_with_active_state(self):
        """Test /cancel with an active state."""
        message = MagicMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.get_state = AsyncMock(return_value="SomeState:some_state")
        state.clear = AsyncMock()

        await cmd_cancel(message, state)

        state.get_state.assert_called_once()
        state.clear.assert_called_once()
        message.answer.assert_called_once()

        # Check cancellation message
        call_args = message.answer.call_args[0][0]
        assert "cancel" in call_args.lower() or "cleared" in call_args.lower()

    @pytest.mark.asyncio
    async def test_cmd_cancel_without_active_state(self):
        """Test /cancel without an active state."""
        message = MagicMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.get_state = AsyncMock(return_value=None)
        state.clear = AsyncMock()

        await cmd_cancel(message, state)

        state.get_state.assert_called_once()
        state.clear.assert_not_called()
        message.answer.assert_called_once()

        # Check message indicates nothing to cancel
        call_args = message.answer.call_args[0][0]
        assert "nothing" in call_args.lower() or "no" in call_args.lower()
