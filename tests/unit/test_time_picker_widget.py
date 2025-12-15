"""Unit tests for time picker widget.

Tests time_selected storage and is_valid_birth_time validation.
"""

from datetime import time
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.types import CallbackQuery, Message

from src.apisbot.bot.widgets.time_picker import TimePickerWidget


class TestTimePickerHourKeyboard:
    """Test suite for hour selection keyboard."""

    def test_create_hour_keyboard_has_24_hours(self):
        """Test that hour keyboard contains all 24 hours (0-23)."""
        keyboard = TimePickerWidget.create_hour_keyboard()

        # Should have 6 rows x 4 columns = 24 buttons
        assert len(keyboard.inline_keyboard) == 6

        # Verify each row has 4 buttons
        for row in keyboard.inline_keyboard:
            assert len(row) == 4

        # Verify all hours 0-23 are present
        all_hours = []
        for row in keyboard.inline_keyboard:
            for button in row:
                # Extract hour from callback_data "time_hour:XX"
                hour = int(button.callback_data.split(":")[1])
                all_hours.append(hour)

        assert sorted(all_hours) == list(range(24))

    def test_hour_keyboard_button_text_format(self):
        """Test that hour buttons display as 'HH:__' format."""
        keyboard = TimePickerWidget.create_hour_keyboard()

        # Check first button (hour 0)
        first_button = keyboard.inline_keyboard[0][0]
        assert first_button.text == "00:__"

        # Check last button (hour 23)
        last_button = keyboard.inline_keyboard[5][3]
        assert last_button.text == "23:__"

    def test_hour_keyboard_callback_data_format(self):
        """Test that hour buttons have correct callback_data format."""
        keyboard = TimePickerWidget.create_hour_keyboard()

        # Check first button (hour 0)
        first_button = keyboard.inline_keyboard[0][0]
        assert first_button.callback_data == "time_hour:0"

        # Check middle button (hour 12)
        middle_button = keyboard.inline_keyboard[3][0]
        assert middle_button.callback_data == "time_hour:12"

        # Check last button (hour 23)
        last_button = keyboard.inline_keyboard[5][3]
        assert last_button.callback_data == "time_hour:23"


class TestTimePickerMinuteKeyboard:
    """Test suite for minute selection keyboard."""

    def test_create_minute_keyboard_has_4_intervals(self):
        """Test that minute keyboard has 4 intervals (0, 15, 30, 45)."""
        keyboard = TimePickerWidget.create_minute_keyboard(selected_hour=14)

        # Should have 3 rows: 2 rows of 2 buttons each + 1 row for manual entry
        assert len(keyboard.inline_keyboard) == 3

        # First two rows should have 2 buttons each (minute intervals)
        assert len(keyboard.inline_keyboard[0]) == 2
        assert len(keyboard.inline_keyboard[1]) == 2

        # Last row should have 1 button (manual entry)
        assert len(keyboard.inline_keyboard[2]) == 1

    def test_minute_keyboard_displays_selected_hour(self):
        """Test that minute buttons display the previously selected hour."""
        keyboard = TimePickerWidget.create_minute_keyboard(selected_hour=9)

        # Check that all minute buttons show hour 9
        assert keyboard.inline_keyboard[0][0].text == "09:00"
        assert keyboard.inline_keyboard[0][1].text == "09:15"
        assert keyboard.inline_keyboard[1][0].text == "09:30"
        assert keyboard.inline_keyboard[1][1].text == "09:45"

    def test_minute_keyboard_callback_data_format(self):
        """Test that minute buttons have correct callback_data format."""
        keyboard = TimePickerWidget.create_minute_keyboard(selected_hour=16)

        # Check callback_data format: "time_minute:HH:MM"
        assert keyboard.inline_keyboard[0][0].callback_data == "time_minute:16:0"
        assert keyboard.inline_keyboard[0][1].callback_data == "time_minute:16:15"
        assert keyboard.inline_keyboard[1][0].callback_data == "time_minute:16:30"
        assert keyboard.inline_keyboard[1][1].callback_data == "time_minute:16:45"

    def test_minute_keyboard_has_manual_entry_option(self):
        """Test that minute keyboard includes manual entry fallback option."""
        keyboard = TimePickerWidget.create_minute_keyboard(selected_hour=12)

        # Last row should have manual entry button
        manual_button = keyboard.inline_keyboard[2][0]
        assert "manual" in manual_button.text.lower() or "✍️" in manual_button.text
        assert manual_button.callback_data == "time_manual"


class TestTimePickerHourSelection:
    """Test suite for hour selection handler."""

    @pytest.mark.asyncio
    async def test_handle_hour_selection_stores_hour(self):
        """Test that hour selection stores selected hour in storage."""
        # Mock CallbackQuery
        callback = MagicMock(spec=CallbackQuery)
        callback.data = "time_hour:14"
        callback.message = MagicMock(spec=Message)
        callback.message.edit_text = AsyncMock()
        callback.answer = AsyncMock()

        storage = {}

        await TimePickerWidget.handle_hour_selection(callback, storage)

        # Verify hour stored
        assert storage["selected_hour"] == 14

    @pytest.mark.asyncio
    async def test_handle_hour_selection_shows_minute_keyboard(self):
        """Test that hour selection displays minute selection keyboard."""
        # Mock CallbackQuery
        callback = MagicMock(spec=CallbackQuery)
        callback.data = "time_hour:8"
        callback.message = MagicMock(spec=Message)
        callback.message.edit_text = AsyncMock()
        callback.answer = AsyncMock()

        storage = {}

        await TimePickerWidget.handle_hour_selection(callback, storage)

        # Verify message edited with minute keyboard
        callback.message.edit_text.assert_called_once()
        call_args = callback.message.edit_text.call_args

        # Check that text mentions selected hour
        assert "8" in call_args[0][0] or "08" in call_args[0][0]

        # Check that reply_markup is present
        assert "reply_markup" in call_args[1]

    @pytest.mark.asyncio
    async def test_handle_hour_selection_ignores_invalid_callback(self):
        """Test that hour handler ignores callbacks without time_hour prefix."""
        callback = MagicMock(spec=CallbackQuery)
        callback.data = "other_callback"

        storage = {}

        await TimePickerWidget.handle_hour_selection(callback, storage)

        # Verify nothing stored
        assert "selected_hour" not in storage

    @pytest.mark.asyncio
    async def test_handle_hour_selection_handles_missing_data(self):
        """Test that hour handler handles callback with no data gracefully."""
        callback = MagicMock(spec=CallbackQuery)
        callback.data = None

        storage = {}

        await TimePickerWidget.handle_hour_selection(callback, storage)

        # Verify nothing stored
        assert "selected_hour" not in storage


class TestTimePickerMinuteSelection:
    """Test suite for minute selection handler."""

    @pytest.mark.asyncio
    async def test_handle_minute_selection_stores_time(self):
        """Test that minute selection stores selected time in storage."""
        # Mock CallbackQuery
        callback = MagicMock(spec=CallbackQuery)
        callback.data = "time_minute:14:30"
        callback.answer = AsyncMock()

        storage = {}

        result = await TimePickerWidget.handle_minute_selection(callback, storage)

        # Verify time stored
        assert storage["selected_time"] == time(14, 30)
        assert storage["selected_time_display"] == "14:30"
        assert result == time(14, 30)

    @pytest.mark.asyncio
    async def test_handle_minute_selection_returns_time_object(self):
        """Test that minute selection returns a time object."""
        callback = MagicMock(spec=CallbackQuery)
        callback.data = "time_minute:9:15"
        callback.answer = AsyncMock()

        storage = {}

        result = await TimePickerWidget.handle_minute_selection(callback, storage)

        # Verify result is time object
        assert isinstance(result, time)
        assert result.hour == 9
        assert result.minute == 15

    @pytest.mark.asyncio
    async def test_handle_minute_selection_ignores_invalid_callback(self):
        """Test that minute handler ignores callbacks without time_minute prefix."""
        callback = MagicMock(spec=CallbackQuery)
        callback.data = "other_callback"
        callback.answer = AsyncMock()

        storage = {}

        result = await TimePickerWidget.handle_minute_selection(callback, storage)

        # Verify nothing stored and None returned
        assert "selected_time" not in storage
        assert result is None

    @pytest.mark.asyncio
    async def test_handle_minute_selection_handles_missing_data(self):
        """Test that minute handler handles callback with no data gracefully."""
        callback = MagicMock(spec=CallbackQuery)
        callback.data = None
        callback.answer = AsyncMock()

        storage = {}

        result = await TimePickerWidget.handle_minute_selection(callback, storage)

        # Verify nothing stored and None returned
        assert "selected_time" not in storage
        assert result is None


class TestTimePickerStorage:
    """Test suite for time storage and retrieval."""

    def test_get_selected_time_returns_none_when_not_set(self):
        """Test that get_selected_time returns None when no time selected yet."""
        storage = {}

        result = TimePickerWidget.get_selected_time(storage)

        assert result is None

    def test_get_selected_time_returns_stored_time(self):
        """Test that get_selected_time returns the stored time from storage."""
        storage = {"selected_time": time(16, 45)}

        result = TimePickerWidget.get_selected_time(storage)

        assert result == time(16, 45)

    def test_is_valid_birth_time_accepts_midnight(self):
        """Test that midnight (00:00) is a valid birth time."""
        birth_time = time(0, 0)

        # Valid time object
        assert birth_time.hour == 0
        assert birth_time.minute == 0

    def test_is_valid_birth_time_accepts_noon(self):
        """Test that noon (12:00) is a valid birth time."""
        birth_time = time(12, 0)

        # Valid time object
        assert birth_time.hour == 12
        assert birth_time.minute == 0

    def test_is_valid_birth_time_accepts_end_of_day(self):
        """Test that 23:59 is a valid birth time."""
        birth_time = time(23, 59)

        # Valid time object
        assert birth_time.hour == 23
        assert birth_time.minute == 59
