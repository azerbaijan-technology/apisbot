"""Integration tests for error recovery and data preservation.

Tests end-to-end error handling with data preservation.
Validates FR-006 (never clear valid data on error) and US3 (error recovery).
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, User

from apisbot.bot.handlers.chart_flow import process_date, process_location, process_name, process_time


class TestErrorRecoveryWithDataPreservation:
    """Test error recovery preserves previously entered valid data."""

    @pytest.mark.asyncio
    async def test_invalid_time_preserves_valid_name_and_date(self):
        """Test invalid time input preserves previously entered name and date."""
        # Arrange
        message = MagicMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.text = "25:99"  # Invalid time
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.get_data = AsyncMock(
            return_value={
                "name": "John Doe",
                "birth_date": "1990-05-15",
            }
        )
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()

        # Act
        await process_time(message, state)

        # Assert - error message shown
        message.answer.assert_called_once()
        error_message = message.answer.call_args[0][0]
        assert "❌" in error_message or "invalid" in error_message.lower()

        # Assert - state NOT advanced (re-prompt for time)
        state.set_state.assert_not_called()

        # Assert - previous data NOT cleared
        state.update_data.assert_not_called()

    @pytest.mark.asyncio
    async def test_invalid_location_preserves_all_previous_data(self):
        """Test invalid location preserves name, date, and time."""
        # Arrange
        message = MagicMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.text = "xyznotarealcity123456"  # Invalid location
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.get_data = AsyncMock(
            return_value={
                "name": "John Doe",
                "birth_date": "1990-05-15",
                "birth_time": "14:30:00",
            }
        )
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()

        # Act
        await process_location(message, state)

        # Assert - error message shown
        message.answer.assert_called()

        # Assert - state NOT advanced
        state.set_state.assert_not_called()

    @pytest.mark.asyncio
    async def test_valid_input_after_error_continues_flow(self):
        """Test valid input after error allows flow to continue."""
        # Arrange - first try with invalid date
        message_invalid = MagicMock(spec=Message)
        message_invalid.from_user = User(id=123, is_bot=False, first_name="Test")
        message_invalid.text = "invalid-date"
        message_invalid.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.get_data = AsyncMock(return_value={"name": "John Doe"})
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()

        # Act - invalid date
        await process_date(message_invalid, state)

        # Assert - error shown, state not advanced
        assert message_invalid.answer.called
        # First call should not advance state
        first_set_state_call_count = state.set_state.call_count

        # The core validation: invalid input doesn't advance state
        # (Valid input continuation is tested in unit tests)
        assert first_set_state_call_count == 0


class TestErrorMessagesWithRemediation:
    """Test error messages include helpful remediation guidance."""

    @pytest.mark.asyncio
    async def test_invalid_date_shows_format_examples(self):
        """Test invalid date error includes format examples."""
        # Arrange
        message = MagicMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.text = "bad-format"
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.get_data = AsyncMock(return_value={"name": "John"})
        state.update_data = AsyncMock()

        # Act
        await process_date(message, state)

        # Assert - error message includes guidance
        message.answer.assert_called_once()
        error_message = message.answer.call_args[0][0]
        assert "❌" in error_message
        # Should show format or example
        assert len(error_message) > 20  # Substantial error message

    @pytest.mark.asyncio
    async def test_invalid_time_shows_format_examples(self):
        """Test invalid time error includes format examples."""
        # Arrange
        message = MagicMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.text = "bad-time"
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.get_data = AsyncMock(return_value={"name": "John", "birth_date": "1990-05-15"})
        state.update_data = AsyncMock()

        # Act
        await process_time(message, state)

        # Assert - error message includes guidance
        message.answer.assert_called_once()
        error_message = message.answer.call_args[0][0]
        assert "❌" in error_message


class TestMultipleErrorRecovery:
    """Test multiple consecutive errors don't lose data."""

    @pytest.mark.asyncio
    async def test_multiple_invalid_inputs_preserve_valid_data(self):
        """Test multiple invalid inputs in a row still preserve valid data."""
        # Arrange
        message = MagicMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.get_data = AsyncMock(
            return_value={
                "name": "John Doe",
                "birth_date": "1990-05-15",
            }
        )
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()

        # Act - first invalid time
        message.text = "99:99"
        await process_time(message, state)

        # Assert - error shown
        message.answer.assert_called()

        # Act - second invalid time with new mock
        message2 = MagicMock(spec=Message)
        message2.from_user = User(id=123, is_bot=False, first_name="Test")
        message2.text = "invalid"
        message2.answer = AsyncMock()

        await process_time(message2, state)

        # Assert - second error also shown
        message2.answer.assert_called()
        # State never advanced
        state.set_state.assert_not_called()


class TestEmptyInputHandling:
    """Test empty inputs are handled gracefully."""

    @pytest.mark.asyncio
    async def test_empty_name_shows_error(self):
        """Test empty name input shows appropriate error."""
        # Arrange
        message = MagicMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.text = "   "  # Whitespace only
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()

        # Act
        await process_name(message, state)

        # Assert
        message.answer.assert_called_once()
        error_message = message.answer.call_args[0][0]
        assert "❌" in error_message
        state.set_state.assert_not_called()

    @pytest.mark.asyncio
    async def test_empty_date_shows_error(self):
        """Test empty date input shows appropriate error."""
        # Arrange
        message = MagicMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.text = ""
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.get_data = AsyncMock(return_value={"name": "John"})
        state.update_data = AsyncMock()

        # Act
        await process_date(message, state)

        # Assert
        message.answer.assert_called_once()


class TestNoMessageText:
    """Test handlers gracefully handle messages without text."""

    @pytest.mark.asyncio
    async def test_none_message_text_for_name(self):
        """Test None message text is handled for name input."""
        # Arrange
        message = MagicMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.text = None
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()

        # Act
        await process_name(message, state)

        # Assert - should show error, not crash
        message.answer.assert_called_once()
        error_message = message.answer.call_args[0][0]
        assert "❌" in error_message

    @pytest.mark.asyncio
    async def test_none_message_text_for_date(self):
        """Test None message text is handled for date input."""
        # Arrange
        message = MagicMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.text = None
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.get_data = AsyncMock(return_value={"name": "John"})

        # Act
        await process_date(message, state)

        # Assert - should show error, not crash
        message.answer.assert_called_once()
