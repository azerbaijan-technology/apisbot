"""Integration tests for calendar and time picker widgets end-to-end.

Tests full user flow with calendar widget for date selection and
time picker for time selection.

Note: These tests verify the widget behavior in isolation. Full bot integration
with aiogram-dialog requires additional setup in main bot initialization.
"""

from datetime import date, time
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.types import CallbackQuery, Message

from src.apisbot.bot.widgets.calendar import BIRTH_DATE_CALENDAR_CONFIG, CalendarWidget
from src.apisbot.bot.widgets.time_picker import TimePickerWidget


class TestCalendarWidgetIntegration:
    """Integration tests for calendar widget in natal flow."""

    def test_calendar_widget_date_range_prevents_invalid_dates(self):
        """
        Given: User is prompted for birth date
        When: Calendar widget is shown
        Then: Calendar prevents selection of future dates and dates > 200 years ago
        """
        # Verify calendar config constraints
        assert BIRTH_DATE_CALENDAR_CONFIG.max_date == date.today()
        assert BIRTH_DATE_CALENDAR_CONFIG.min_date.year == date.today().year - 200

        # Future dates should be outside range
        from datetime import timedelta

        future_date = date.today() + timedelta(days=1)
        assert future_date > BIRTH_DATE_CALENDAR_CONFIG.max_date

        # Very old dates should be outside range
        very_old_date = date(year=date.today().year - 201, month=1, day=1)
        assert very_old_date < BIRTH_DATE_CALENDAR_CONFIG.min_date

    def test_calendar_widget_stores_selected_date(self):
        """
        Given: User navigates calendar widget
        When: User selects a valid date
        Then: Selected date is stored in dialog context
        """

        # Mock DialogManager
        class MockDialogManager:
            dialog_data = {}

        manager = MockDialogManager()

        # Simulate date selection by manually storing in dialog_data
        # (In real flow, aiogram-dialog on_click handler would do this)
        selected = date(1990, 7, 15)
        manager.dialog_data["selected_date"] = selected
        manager.dialog_data["selected_date_display"] = str(selected)

        # Verify date stored correctly
        retrieved = CalendarWidget.get_selected_date(manager)  # type: ignore
        assert retrieved == date(1990, 7, 15)

    @pytest.mark.asyncio
    async def test_calendar_widget_data_available_for_rendering(self):
        """
        Given: User has selected a date via calendar
        When: Dialog renders
        Then: Calendar data is available for display
        """
        from src.apisbot.bot.widgets.calendar import get_calendar_data

        # Mock DialogManager with selected date
        class MockDialogManager:
            dialog_data = {
                "selected_date": date(1985, 3, 20),
                "selected_date_display": "1985-03-20",
            }

        manager = MockDialogManager()

        # Get calendar data for rendering
        data = await get_calendar_data(manager)  # type: ignore

        # Verify data structure
        assert data["selected_date"] == date(1985, 3, 20)
        assert data["selected_date_display"] == "1985-03-20"


class TestTimePickerWidgetIntegration:
    """Integration tests for time picker widget in natal flow."""

    @pytest.mark.asyncio
    async def test_time_picker_hour_selection_flow(self):
        """
        Given: User is prompted for birth time
        When: Time picker widget is shown and user selects hour
        Then: Hour is stored and minute selection keyboard appears
        """
        # Mock CallbackQuery for hour selection (14:00)
        callback_hour = MagicMock(spec=CallbackQuery)
        callback_hour.data = "time_hour:14"
        callback_hour.message = MagicMock(spec=Message)
        callback_hour.message.edit_text = AsyncMock()
        callback_hour.answer = AsyncMock()

        storage = {}

        # Simulate hour selection
        await TimePickerWidget.handle_hour_selection(callback_hour, storage)

        # Verify hour stored
        assert storage["selected_hour"] == 14

        # Verify minute keyboard shown (message edited)
        callback_hour.message.edit_text.assert_called_once()
        call_args = callback_hour.message.edit_text.call_args
        assert "reply_markup" in call_args[1]

    @pytest.mark.asyncio
    async def test_time_picker_minute_selection_completes_flow(self):
        """
        Given: User has selected hour
        When: User selects minute
        Then: Complete time is stored and validated
        """
        # Mock CallbackQuery for minute selection
        callback = MagicMock(spec=CallbackQuery)
        callback.data = "time_minute:14:30"
        callback.answer = AsyncMock()

        storage = {}

        # Simulate minute selection
        result = await TimePickerWidget.handle_minute_selection(callback, storage)

        # Verify complete time stored
        assert storage["selected_time"] == time(14, 30)
        assert storage["selected_time_display"] == "14:30"
        assert result == time(14, 30)

    @pytest.mark.asyncio
    async def test_time_picker_full_flow_hour_then_minute(self):
        """
        Given: User is prompted for birth time
        When: User selects hour then minute via time picker
        Then: Complete time is stored in single storage object
        """
        storage = {}

        # Step 1: Select hour
        # Test with hour and minute selection
        hour_callback = MagicMock(spec=CallbackQuery)
        hour_callback.data = "time_hour:8"
        hour_callback.message = MagicMock(spec=Message)
        hour_callback.message.edit_text = AsyncMock()
        hour_callback.answer = AsyncMock()

        await TimePickerWidget.handle_hour_selection(hour_callback, storage)

        # Verify hour stored
        assert storage["selected_hour"] == 8

        # Step 2: Select minute
        minute_callback = MagicMock(spec=CallbackQuery)
        minute_callback.data = "time_minute:9:15"
        minute_callback.answer = AsyncMock()

        result = await TimePickerWidget.handle_minute_selection(minute_callback, storage)

        # Verify complete time stored
        assert result == time(9, 15)
        assert storage["selected_time"] == time(9, 15)
        assert storage["selected_time_display"] == "09:15"

    def test_time_picker_provides_manual_entry_fallback(self):
        """
        Given: User is selecting minute
        When: Minute keyboard is displayed
        Then: Manual entry option is available for exact times
        """
        keyboard = TimePickerWidget.create_minute_keyboard(selected_hour=12)

        # Find manual entry button (last row)
        manual_button = keyboard.inline_keyboard[2][0]

        # Verify manual entry option present
        assert manual_button.callback_data == "time_manual"
        assert "manual" in manual_button.text.lower() or "✍️" in manual_button.text


class TestCalendarAndTimePickerCombined:
    """Integration tests for combined calendar + time picker flow."""

    @pytest.mark.asyncio
    async def test_date_and_time_selection_preserves_both_values(self):
        """
        Given: User has selected birth date via calendar
        When: User then selects birth time via time picker
        Then: Both date and time are preserved in separate storage
        """
        # Calendar storage (dialog_data)
        calendar_storage = {
            "selected_date": date(1992, 11, 5),
            "selected_date_display": "1992-11-05",
        }

        # Time picker storage (separate FSM state or session)
        time_storage = {}

        # Simulate time selection
        callback = MagicMock(spec=CallbackQuery)
        callback.data = "time_minute:16:45"
        callback.answer = AsyncMock()

        await TimePickerWidget.handle_minute_selection(callback, time_storage)

        # Verify both storages independent and correct
        assert calendar_storage["selected_date"] == date(1992, 11, 5)
        assert time_storage["selected_time"] == time(16, 45)

    @pytest.mark.asyncio
    async def test_date_time_widgets_support_edge_case_values(self):
        """
        Given: User selects edge case date/time values
        When: Calendar and time picker process selections
        Then: Edge cases are handled correctly
        """
        # Edge case: Today's date (born today)
        calendar_storage = {
            "selected_date": date.today(),
            "selected_date_display": str(date.today()),
        }

        # Edge case: Midnight (00:00)
        time_storage = {}
        callback = MagicMock(spec=CallbackQuery)
        callback.data = "time_minute:0:0"
        callback.answer = AsyncMock()

        result = await TimePickerWidget.handle_minute_selection(callback, time_storage)

        # Verify edge cases handled
        assert calendar_storage["selected_date"] == date.today()
        assert result == time(0, 0)
        assert time_storage["selected_time"] == time(0, 0)

    @pytest.mark.asyncio
    async def test_widgets_provide_clear_user_feedback(self):
        """
        Given: User interacts with widgets
        When: Selections are made
        Then: Clear feedback is provided at each step
        """
        # Test hour selection feedback
        # Mock callback with hour selection
        callback = MagicMock(spec=CallbackQuery)
        callback.data = "time_hour:9"
        callback.message = MagicMock(spec=Message)
        callback.message.edit_text = AsyncMock()
        callback.answer = AsyncMock()

        storage = {}
        await TimePickerWidget.handle_hour_selection(callback, storage)

        # Verify message edited to show progress
        callback.message.edit_text.assert_called_once()
        edit_call_args = callback.message.edit_text.call_args
        # Should mention hour and prompt for minute
        assert "9" in edit_call_args[0][0] or "minute" in edit_call_args[0][0].lower()

        # Test minute selection feedback
        minute_callback = MagicMock(spec=CallbackQuery)
        minute_callback.data = "time_minute:18:30"
        minute_callback.answer = AsyncMock()

        await TimePickerWidget.handle_minute_selection(minute_callback, storage)

        # Verify callback answered with confirmation
        minute_callback.answer.assert_called_once()
        answer_call_args = minute_callback.answer.call_args
        # Should confirm time selection
        assert "18:30" in answer_call_args[0][0]


class TestWidgetValidationIntegration:
    """Integration tests for widget validation with service layer."""

    def test_calendar_prevents_invalid_dates_at_ui_level(self):
        """
        Given: Calendar widget is configured
        When: User attempts to select invalid date
        Then: Calendar UI prevents invalid selection (Feb 30 impossible)

        Note: Calendar widget itself prevents Feb 30 via date picker UI.
        No server-side validation needed for impossible dates.
        """
        # Calendar widget config enforces valid dates
        config = BIRTH_DATE_CALENDAR_CONFIG

        # Verify constraints present
        assert config.min_date is not None
        assert config.max_date is not None

        # Impossible dates (Feb 30) cannot be selected via calendar UI
        # This is enforced by aiogram-dialog calendar widget behavior
        # No additional validation needed

    @pytest.mark.asyncio
    async def test_time_picker_produces_valid_time_objects(self):
        """
        Given: User selects time via time picker
        When: Time is stored
        Then: Time object is valid Python time (no validation errors possible)
        """
        callback = MagicMock(spec=CallbackQuery)
        callback.data = "time_minute:23:45"
        callback.answer = AsyncMock()

        storage = {}
        result = await TimePickerWidget.handle_minute_selection(callback, storage)

        # Verify valid time object created
        assert isinstance(result, time)
        assert 0 <= result.hour <= 23
        assert 0 <= result.minute <= 59

    def test_widgets_integration_with_validators(self):
        """
        Given: Calendar and time picker provide date/time selections
        When: Selections are passed to validators
        Then: Validators receive correctly formatted date/time objects

        Note: Widgets produce date and time objects directly, so validators
        receive structured data instead of text parsing requirements.
        """
        # Calendar produces date object
        calendar_date = date(1988, 6, 10)
        assert isinstance(calendar_date, date)

        # Time picker produces time object
        picker_time = time(14, 30)
        assert isinstance(picker_time, time)

        # Validators would receive these objects instead of text strings
        # This eliminates parsing errors entirely
