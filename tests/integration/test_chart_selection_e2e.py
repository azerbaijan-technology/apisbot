"""Integration tests for chart selection flow.

Tests end-to-end chart type selection and routing to appropriate flows.
Validates US2 (chart selection menu navigation).
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, User

from apisbot.bot.handlers.start import cmd_start, handle_chart_selection
from apisbot.bot.states import ChartFlow, CompositeFlow
from apisbot.models.chart_selection import ChartSelection


class TestChartSelectionFlowE2E:
    """End-to-end tests for chart selection flow."""

    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.start.session_service")
    async def test_user_sends_start_and_sees_natal_button(self, mock_session_service):
        """Test /start displays Natal Chart button."""
        # Arrange
        mock_session_service.clear_session = AsyncMock()

        message = MagicMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.clear = AsyncMock()

        # Act
        await cmd_start(message, state)

        # Assert
        call_args = message.answer.call_args
        keyboard = call_args[1]["reply_markup"]

        # Find Natal button
        natal_button_found = False
        for row in keyboard.inline_keyboard:
            for button in row:
                if "natal" in button.callback_data.lower():
                    natal_button_found = True
                    assert "Natal" in button.text
                    break

        assert natal_button_found, "Natal Chart button not found in menu"

    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.start.session_service")
    async def test_user_sends_start_and_sees_composite_button(self, mock_session_service):
        """Test /start displays Composite Chart button."""
        # Arrange
        mock_session_service.clear_session = AsyncMock()

        message = MagicMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.clear = AsyncMock()

        # Act
        await cmd_start(message, state)

        # Assert
        call_args = message.answer.call_args
        keyboard = call_args[1]["reply_markup"]

        # Find Composite button
        composite_button_found = False
        for row in keyboard.inline_keyboard:
            for button in row:
                if "composite" in button.callback_data.lower():
                    composite_button_found = True
                    assert "Composite" in button.text
                    break

        assert composite_button_found, "Composite Chart button not found in menu"

    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.start.session_service")
    async def test_clicking_natal_button_starts_natal_flow(self, mock_session_service):
        """Test clicking Natal Chart button transitions to natal flow."""
        # Arrange
        from apisbot.models.session import UserSession

        mock_session = UserSession(user_id=123, chart_type=None)
        mock_session_service.get_or_create_session = AsyncMock(return_value=mock_session)

        callback = MagicMock(spec=CallbackQuery)
        callback.from_user = User(id=123, is_bot=False, first_name="Test")
        callback.data = f"chart_select:{ChartSelection.NATAL.value}"
        callback.message = MagicMock()
        callback.message.edit_text = AsyncMock()
        callback.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.set_state = AsyncMock()

        # Act
        await handle_chart_selection(callback, state)

        # Assert - verify transition to natal flow
        state.set_state.assert_called_once_with(ChartFlow.waiting_for_name)
        callback.message.edit_text.assert_called_once()

        # Verify message mentions natal chart
        edit_call_args = callback.message.edit_text.call_args[0][0]
        assert "Natal" in edit_call_args

    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.start.session_service")
    async def test_clicking_composite_button_starts_composite_flow(self, mock_session_service):
        """Test clicking Composite Chart button transitions to composite flow."""
        # Arrange
        from apisbot.models.session import UserSession

        mock_session = UserSession(user_id=123, chart_type=None)
        mock_session_service.get_or_create_session = AsyncMock(return_value=mock_session)

        callback = MagicMock(spec=CallbackQuery)
        callback.from_user = User(id=123, is_bot=False, first_name="Test")
        callback.data = f"chart_select:{ChartSelection.COMPOSITE.value}"
        callback.message = MagicMock()
        callback.message.edit_text = AsyncMock()
        callback.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.set_state = AsyncMock()

        # Act
        await handle_chart_selection(callback, state)

        # Assert - verify transition to composite flow
        state.set_state.assert_called_once_with(CompositeFlow.waiting_for_name_1)
        callback.message.edit_text.assert_called_once()

        # Verify message mentions composite chart
        edit_call_args = callback.message.edit_text.call_args[0][0]
        assert "Composite" in edit_call_args

    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.start.session_service")
    async def test_chart_selection_stores_choice_in_session(self, mock_session_service):
        """Test chart selection stores the choice in user session."""
        # Arrange
        from apisbot.models.session import UserSession

        mock_session = UserSession(user_id=123, chart_type=None)
        mock_session_service.get_or_create_session = AsyncMock(return_value=mock_session)

        callback = MagicMock(spec=CallbackQuery)
        callback.from_user = User(id=123, is_bot=False, first_name="Test")
        callback.data = f"chart_select:{ChartSelection.NATAL.value}"
        callback.message = MagicMock()
        callback.message.edit_text = AsyncMock()
        callback.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.set_state = AsyncMock()

        # Act
        await handle_chart_selection(callback, state)

        # Assert - verify session was retrieved
        mock_session_service.get_or_create_session.assert_called_once_with(123)

        # Verify chart type was stored in session
        assert mock_session.chart_type == ChartSelection.NATAL


class TestChartSelectionErrorHandling:
    """Test error handling in chart selection flow."""

    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.start.session_service")
    async def test_invalid_chart_type_shows_error(self, mock_session_service):
        """Test invalid chart type shows error to user."""
        # Arrange
        from apisbot.models.session import UserSession

        mock_session = UserSession(user_id=123, chart_type=None)
        mock_session_service.get_or_create_session = AsyncMock(return_value=mock_session)

        callback = MagicMock(spec=CallbackQuery)
        callback.from_user = User(id=123, is_bot=False, first_name="Test")
        callback.data = "chart_select:invalid_type"
        callback.message = MagicMock()
        callback.message.edit_text = AsyncMock()
        callback.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.set_state = AsyncMock()

        # Act
        await handle_chart_selection(callback, state)

        # Assert - verify error was shown
        callback.answer.assert_called_once()
        answer_call = callback.answer.call_args

        # Should show alert for invalid selection
        assert answer_call[1].get("show_alert") is True

    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.start.session_service")
    async def test_missing_callback_data_handled_gracefully(self, mock_session_service):
        """Test missing callback data is handled gracefully."""
        # Arrange
        callback = MagicMock(spec=CallbackQuery)
        callback.from_user = User(id=123, is_bot=False, first_name="Test")
        callback.data = None
        callback.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)

        # Act
        await handle_chart_selection(callback, state)

        # Assert - should handle gracefully
        callback.answer.assert_called_once_with("Invalid selection")


class TestChartSelectionUserExperience:
    """Test user experience aspects of chart selection."""

    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.start.session_service")
    async def test_natal_selection_shows_required_information(self, mock_session_service):
        """Test natal selection shows what information is needed."""
        # Arrange
        from apisbot.models.session import UserSession

        mock_session = UserSession(user_id=123, chart_type=None)
        mock_session_service.get_or_create_session = AsyncMock(return_value=mock_session)

        callback = MagicMock(spec=CallbackQuery)
        callback.from_user = User(id=123, is_bot=False, first_name="Test")
        callback.data = f"chart_select:{ChartSelection.NATAL.value}"
        callback.message = MagicMock()
        callback.message.edit_text = AsyncMock()
        callback.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.set_state = AsyncMock()

        # Act
        await handle_chart_selection(callback, state)

        # Assert - message should explain what's needed
        message_text = callback.message.edit_text.call_args[0][0]
        assert "Name" in message_text or "name" in message_text
        assert "date" in message_text.lower()
        assert "time" in message_text.lower()
        assert "location" in message_text.lower()

    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.start.session_service")
    async def test_composite_selection_shows_two_people_needed(self, mock_session_service):
        """Test composite selection clarifies two people's data is needed."""
        # Arrange
        from apisbot.models.session import UserSession

        mock_session = UserSession(user_id=123, chart_type=None)
        mock_session_service.get_or_create_session = AsyncMock(return_value=mock_session)

        callback = MagicMock(spec=CallbackQuery)
        callback.from_user = User(id=123, is_bot=False, first_name="Test")
        callback.data = f"chart_select:{ChartSelection.COMPOSITE.value}"
        callback.message = MagicMock()
        callback.message.edit_text = AsyncMock()
        callback.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.set_state = AsyncMock()

        # Act
        await handle_chart_selection(callback, state)

        # Assert - message should mention two people
        message_text = callback.message.edit_text.call_args[0][0]
        assert "two" in message_text.lower() or "2" in message_text or "Person 1" in message_text
