"""Integration tests for start menu and help documentation.

Tests end-to-end user flows for chart selection menu and help system.
Validates FR-003 (help documentation) and US1 (menu hints).
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message, User

from apisbot.bot.handlers.start import (
    cmd_help,
    cmd_start,
    handle_chart_selection,
    handle_help_button,
)
from apisbot.models.chart_selection import ChartSelection
from apisbot.services.menu_service import MenuService


class TestStartMenuE2E:
    """End-to-end tests for /start menu."""

    @pytest.mark.asyncio
    async def test_start_command_displays_chart_selection_menu(self):
        """Test /start displays menu with Natal and Composite chart buttons."""
        # Arrange
        message = MagicMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.clear = AsyncMock()

        # Act
        await cmd_start(message, state)

        # Assert
        state.clear.assert_called_once()
        message.answer.assert_called_once()

        # Verify message content includes chart descriptions
        call_args = message.answer.call_args
        message_text = call_args[0][0]

        assert "Welcome" in message_text
        assert "Natal Chart" in message_text
        assert "Composite Chart" in message_text
        assert ChartSelection.NATAL.description in message_text
        assert ChartSelection.COMPOSITE.description in message_text

        # Verify inline keyboard was provided
        assert "reply_markup" in call_args[1]
        keyboard = call_args[1]["reply_markup"]
        assert isinstance(keyboard, InlineKeyboardMarkup)

    @pytest.mark.asyncio
    async def test_start_menu_includes_help_button(self):
        """Test /start menu includes help button."""
        # Arrange
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

        # Check that keyboard has buttons
        assert len(keyboard.inline_keyboard) > 0

        # Find help button by checking callback data
        help_button_found = False
        for row in keyboard.inline_keyboard:
            for button in row:
                if button.callback_data and "help" in button.callback_data:
                    help_button_found = True
                    assert "Help" in button.text or "help" in button.text.lower()
                    break

        assert help_button_found, "Help button not found in keyboard"

    @pytest.mark.asyncio
    async def test_start_menu_includes_natal_chart_button(self):
        """Test /start menu includes Natal Chart selection button."""
        # Arrange
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

        # Find natal button
        natal_button_found = False
        for row in keyboard.inline_keyboard:
            for button in row:
                if button.callback_data == f"chart_select:{ChartSelection.NATAL.value}":
                    natal_button_found = True
                    assert "Natal" in button.text
                    break

        assert natal_button_found, "Natal Chart button not found"

    @pytest.mark.asyncio
    async def test_start_menu_includes_composite_chart_button(self):
        """Test /start menu includes Composite Chart selection button."""
        # Arrange
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

        # Find composite button
        composite_button_found = False
        for row in keyboard.inline_keyboard:
            for button in row:
                if button.callback_data == f"chart_select:{ChartSelection.COMPOSITE.value}":
                    composite_button_found = True
                    assert "Composite" in button.text
                    break

        assert composite_button_found, "Composite Chart button not found"


class TestHelpDocumentationE2E:
    """End-to-end tests for help documentation system."""

    @pytest.mark.asyncio
    async def test_help_command_displays_comprehensive_documentation(self):
        """Test /help command displays comprehensive help documentation."""
        # Arrange
        message = MagicMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        # Act
        await cmd_help(message)

        # Assert
        message.answer.assert_called_once()
        help_text = message.answer.call_args[0][0]

        # Verify comprehensive documentation
        assert "Natal Chart" in help_text
        assert "Composite Chart" in help_text
        assert "/start" in help_text
        assert "/help" in help_text
        assert "/cancel" in help_text

        # Verify date/time format documentation
        assert "DD.MM.YYYY" in help_text or "date format" in help_text.lower()
        assert "HH:MM" in help_text or "time format" in help_text.lower()

        # Verify location guidance
        assert "location" in help_text.lower() or "city" in help_text.lower()

        # Verify privacy information
        assert "Privacy" in help_text or "data" in help_text.lower()
        assert "30 minutes" in help_text or "session" in help_text.lower()

    @pytest.mark.asyncio
    async def test_help_button_callback_shows_documentation(self):
        """Test help button callback displays comprehensive documentation."""
        # Arrange
        callback = MagicMock(spec=CallbackQuery)
        callback.from_user = User(id=123, is_bot=False, first_name="Test")
        callback.message = MagicMock()
        callback.message.answer = AsyncMock()
        callback.answer = AsyncMock()
        callback.data = "show_help"

        # Act
        await handle_help_button(callback)

        # Assert
        callback.answer.assert_called_once()
        callback.message.answer.assert_called_once()

        # Verify help documentation was displayed
        answer_args = callback.message.answer.call_args
        help_text = answer_args[0][0]

        assert "Natal Chart" in help_text
        assert "Composite Chart" in help_text
        assert "/start" in help_text

    @pytest.mark.asyncio
    async def test_help_documentation_includes_chart_explanations(self):
        """Test help documentation includes explanations of chart types."""
        # Arrange
        message = MagicMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        # Act
        await cmd_help(message)

        # Assert
        help_text = message.answer.call_args[0][0]

        # Check chart type explanations
        assert "natal chart" in help_text.lower() or "birth chart" in help_text.lower()
        assert "composite chart" in help_text.lower()
        assert "relationship" in help_text.lower() or "compatibility" in help_text.lower()

    @pytest.mark.asyncio
    async def test_help_documentation_includes_step_by_step_guide(self):
        """Test help documentation includes step-by-step usage guide."""
        # Arrange
        message = MagicMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        # Act
        await cmd_help(message)

        # Assert
        help_text = message.answer.call_args[0][0]

        # Check step-by-step guide elements
        assert "birth date" in help_text.lower()
        assert "birth time" in help_text.lower()
        assert "birth location" in help_text.lower() or "location" in help_text.lower()


class TestInlineKeyboardHints:
    """Tests for inline keyboard command hints in various states."""

    @pytest.mark.asyncio
    async def test_start_menu_message_mentions_help_availability(self):
        """Test that start menu message mentions help is available."""
        # Arrange
        message = MagicMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.clear = AsyncMock()

        # Act
        await cmd_start(message, state)

        # Assert
        message_text = message.answer.call_args[0][0]
        assert "/help" in message_text, "Start menu should mention /help command"

    @pytest.mark.asyncio
    async def test_menu_service_provides_state_specific_hints(self):
        """Test MenuService provides appropriate hints for different states."""
        # This is a service-level integration test
        states_to_test = [
            "chart_selection",
            "name_entry",
            "date_entry",
            "time_entry",
            "location_entry",
            "generating",
        ]

        for state_name in states_to_test:
            hints = MenuService.get_state_hints(state_name)
            assert len(hints) > 0, f"No hints returned for state: {state_name}"
            assert isinstance(hints, list), f"Hints should be a list for state: {state_name}"


class TestChartSelectionFlow:
    """Test chart selection callback flow."""

    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.start.session_service")
    async def test_natal_chart_selection_callback(self, mock_session_service):
        """Test selecting Natal Chart from menu starts natal flow."""
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

        # Assert
        callback.answer.assert_called_once()
        callback.message.edit_text.assert_called_once()

        # Verify state transition occurred
        state.set_state.assert_called_once()

    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.start.session_service")
    async def test_composite_chart_selection_callback(self, mock_session_service):
        """Test selecting Composite Chart from menu starts composite flow."""
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

        # Assert
        callback.answer.assert_called_once()
        callback.message.edit_text.assert_called_once()

        # Verify state transition occurred
        state.set_state.assert_called_once()


class TestSessionManagement:
    """Test session management in start menu flow."""

    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.start.session_service")
    async def test_start_command_clears_existing_session(self, mock_session_service):
        """Test /start clears any existing user session."""
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
        mock_session_service.clear_session.assert_called_once_with(123)
        state.clear.assert_called_once()
