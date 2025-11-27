"""Tests for common handler helper functions."""

from unittest.mock import patch

from apisbot.bot.handlers.common import (
    create_hint_keyboard,
    get_command_hints,
    get_state_prompt_with_hints,
)


class TestGetCommandHints:
    """Test get_command_hints function."""

    @patch("apisbot.bot.handlers.common.MenuService")
    def test_get_command_hints_with_hints(self, mock_menu_service):
        """Test getting hints when hints are available."""
        mock_menu_service.get_state_hints.return_value = [
            "Use /help for assistance",
            "Use /cancel to abort",
        ]

        result = get_command_hints("date_entry")

        assert "💡 Use /help for assistance" in result
        assert "💡 Use /cancel to abort" in result
        mock_menu_service.get_state_hints.assert_called_once_with("date_entry")

    @patch("apisbot.bot.handlers.common.MenuService")
    def test_get_command_hints_no_hints(self, mock_menu_service):
        """Test getting hints when no hints are available."""
        mock_menu_service.get_state_hints.return_value = []

        result = get_command_hints("unknown_state")

        assert result == ""
        mock_menu_service.get_state_hints.assert_called_once_with("unknown_state")

    @patch("apisbot.bot.handlers.common.MenuService")
    def test_get_command_hints_none_returned(self, mock_menu_service):
        """Test getting hints when None is returned."""
        mock_menu_service.get_state_hints.return_value = None

        result = get_command_hints("some_state")

        assert result == ""


class TestCreateHintKeyboard:
    """Test create_hint_keyboard function."""

    def test_create_hint_keyboard_with_cancel(self):
        """Test creating keyboard with cancel button."""
        keyboard = create_hint_keyboard("date_entry", include_cancel=True)

        assert keyboard is not None
        assert len(keyboard.inline_keyboard) == 2  # Help and Cancel buttons
        assert keyboard.inline_keyboard[0][0].text == "❓ Help"
        assert keyboard.inline_keyboard[1][0].text == "❌ Cancel"

    def test_create_hint_keyboard_without_cancel(self):
        """Test creating keyboard without cancel button."""
        keyboard = create_hint_keyboard("date_entry", include_cancel=False)

        assert keyboard is not None
        assert len(keyboard.inline_keyboard) == 1  # Only Help button
        assert keyboard.inline_keyboard[0][0].text == "❓ Help"

    def test_create_hint_keyboard_callback_data(self):
        """Test that keyboard has correct callback data."""
        keyboard = create_hint_keyboard("date_entry")

        assert keyboard.inline_keyboard[0][0].callback_data == "show_help"
        assert keyboard.inline_keyboard[1][0].callback_data == "cancel_flow"


class TestGetStatePromptWithHints:
    """Test get_state_prompt_with_hints function."""

    @patch("apisbot.bot.handlers.common.get_command_hints")
    def test_get_state_prompt_with_hints(self, mock_get_hints):
        """Test getting prompt with hints appended."""
        mock_get_hints.return_value = "💡 Use /help for assistance"

        result = get_state_prompt_with_hints("date_entry", "Enter your birth date:")

        assert "Enter your birth date:" in result
        assert "💡 Use /help for assistance" in result
        mock_get_hints.assert_called_once_with("date_entry")

    @patch("apisbot.bot.handlers.common.get_command_hints")
    def test_get_state_prompt_without_hints(self, mock_get_hints):
        """Test getting prompt when no hints are available."""
        mock_get_hints.return_value = ""

        result = get_state_prompt_with_hints("unknown_state", "Enter your data:")

        assert result == "Enter your data:"
        mock_get_hints.assert_called_once_with("unknown_state")

    @patch("apisbot.bot.handlers.common.get_command_hints")
    def test_get_state_prompt_formatting(self, mock_get_hints):
        """Test that prompt and hints are properly formatted."""
        mock_get_hints.return_value = "💡 Hint 1\n💡 Hint 2"

        result = get_state_prompt_with_hints("test_state", "Test prompt")

        # Should have prompt, then blank line, then hints
        assert result == "Test prompt\n\n💡 Hint 1\n💡 Hint 2"
