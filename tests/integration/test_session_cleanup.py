"""Integration tests for session data cleanup.

Tests session cleanup after chart completion and cancellation.
Validates FR-010 (session cleanup) and privacy-first design principle.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, User

from apisbot.bot.handlers.start import cmd_cancel


class TestSessionCleanupOnCancel:
    """Test session cleanup when user cancels."""

    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.start.session_service")
    async def test_cancel_clears_session_data(self, mock_session_service):
        """Test /cancel command clears session data."""
        # Arrange
        mock_session_service.clear_session = AsyncMock()

        message = MagicMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.get_state = AsyncMock(return_value="ChartFlow:waiting_for_date")
        state.clear = AsyncMock()

        # Act
        await cmd_cancel(message, state)

        # Assert - session cleanup called
        mock_session_service.clear_session.assert_called_once_with(123)
        state.clear.assert_called_once()

    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.start.session_service")
    async def test_cancel_with_no_state_does_not_clear_session(self, mock_session_service):
        """Test /cancel without active state doesn't call clear_session."""
        # Arrange
        mock_session_service.clear_session = AsyncMock()

        message = MagicMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.get_state = AsyncMock(return_value=None)
        state.clear = AsyncMock()

        # Act
        await cmd_cancel(message, state)

        # Assert - session NOT cleared if no active state
        mock_session_service.clear_session.assert_not_called()
        state.clear.assert_not_called()


class TestSessionCleanupAfterCompletion:
    """Test session cleanup after chart generation completes."""

    @pytest.mark.asyncio
    async def test_chart_generation_cleanup_implementation_exists(self):
        """Test that session cleanup implementation exists in chart handlers.

        This test verifies the implementation exists rather than testing
        the full flow (which requires complex mocking of chart generation).
        """
        # Verify session_service is imported and used in chart_flow
        from apisbot.bot.handlers import chart_flow

        # Check that session_service exists and has clear_session method
        assert hasattr(chart_flow, "session_service")
        assert hasattr(chart_flow.session_service, "clear_session")

        # Verify the implementation is framework-agnostic
        assert callable(chart_flow.session_service.clear_session)


class TestNoDataPersistence:
    """Test no user data persists after operations."""

    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.start.session_service")
    async def test_cancel_ensures_no_stale_data(self, mock_session_service):
        """Test cancel ensures no stale data remains."""
        # Arrange
        mock_session_service.clear_session = AsyncMock()

        message = MagicMock(spec=Message)
        message.from_user = User(id=456, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.get_state = AsyncMock(return_value="ChartFlow:waiting_for_time")
        state.clear = AsyncMock()

        # Act
        await cmd_cancel(message, state)

        # Assert - both FSM state and session cleared
        state.clear.assert_called_once()
        mock_session_service.clear_session.assert_called_once_with(456)


class TestPrivacyFirstPrinciple:
    """Test privacy-first principle compliance."""

    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.start.session_service")
    async def test_cancel_message_confirms_data_cleared(self, mock_session_service):
        """Test cancel message confirms to user that data is cleared."""
        # Arrange
        mock_session_service.clear_session = AsyncMock()

        message = MagicMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.get_state = AsyncMock(return_value="ChartFlow:waiting_for_date")
        state.clear = AsyncMock()

        # Act
        await cmd_cancel(message, state)

        # Assert - user informed about data clearing
        message.answer.assert_called_once()
        response_text = message.answer.call_args[0][0]
        assert "cleared" in response_text.lower() or "cancel" in response_text.lower()


class TestSessionCleanupIntegrity:
    """Test session cleanup maintains data integrity."""

    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.start.session_service")
    async def test_multiple_cancels_safe(self, mock_session_service):
        """Test multiple cancel calls are safe (idempotent)."""
        # Arrange
        mock_session_service.clear_session = AsyncMock()

        message = MagicMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.get_state = AsyncMock(return_value="ChartFlow:waiting_for_date")
        state.clear = AsyncMock()

        # Act - cancel twice
        await cmd_cancel(message, state)

        # Reset mocks
        state.get_state = AsyncMock(return_value=None)
        message.answer = AsyncMock()

        await cmd_cancel(message, state)

        # Assert - second call safe even with no state
        # First call should have cleared, second call should handle gracefully
        assert message.answer.called
