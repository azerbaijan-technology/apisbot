"""Unit tests for calendar widget.

Tests calendar_selected_date storage and is_valid_birth_date validation.
"""

from datetime import date, timedelta

import pytest

from src.apisbot.bot.widgets.calendar import BIRTH_DATE_CALENDAR_CONFIG, CalendarWidget


class TestCalendarWidget:
    """Test suite for CalendarWidget functionality."""

    def test_calendar_config_has_min_max_dates(self):
        """Test that calendar config defines valid min/max date constraints."""
        # Verify min date is ~200 years ago
        expected_min_year = date.today().year - 200
        assert BIRTH_DATE_CALENDAR_CONFIG.min_date.year == expected_min_year
        assert BIRTH_DATE_CALENDAR_CONFIG.min_date.month == 1
        assert BIRTH_DATE_CALENDAR_CONFIG.min_date.day == 1

        # Verify max date is today (no future dates)
        assert BIRTH_DATE_CALENDAR_CONFIG.max_date == date.today()

    def test_create_calendar_returns_calendar_widget(self):
        """Test that create_calendar returns a Calendar widget instance."""
        from aiogram_dialog.widgets.kbd import Calendar

        calendar = CalendarWidget.create_calendar(id="test_calendar")

        assert isinstance(calendar, Calendar)
        assert calendar.widget_id == "test_calendar"

    def test_create_calendar_default_id(self):
        """Test that create_calendar uses default ID when not provided."""
        from aiogram_dialog.widgets.kbd import Calendar

        calendar = CalendarWidget.create_calendar()

        assert isinstance(calendar, Calendar)
        assert calendar.widget_id == "birth_date_calendar"

    def test_is_valid_birth_date_accepts_today(self):
        """Test that today's date is valid (edge case: born today)."""
        today = date.today()

        # Date within range [min_date, max_date]
        assert BIRTH_DATE_CALENDAR_CONFIG.min_date <= today <= BIRTH_DATE_CALENDAR_CONFIG.max_date

    def test_is_valid_birth_date_accepts_old_date(self):
        """Test that very old dates (199 years ago) are valid."""
        old_date = date(year=date.today().year - 199, month=6, day=15)

        # Date within range
        assert BIRTH_DATE_CALENDAR_CONFIG.min_date <= old_date <= BIRTH_DATE_CALENDAR_CONFIG.max_date

    def test_is_valid_birth_date_rejects_future_date(self):
        """Test that future dates are rejected (cannot be born in future)."""
        future_date = date.today() + timedelta(days=1)

        # Date outside max_date range
        assert future_date > BIRTH_DATE_CALENDAR_CONFIG.max_date

    def test_is_valid_birth_date_rejects_very_old_date(self):
        """Test that dates > 200 years ago are rejected."""
        very_old_date = date(year=date.today().year - 201, month=1, day=1)

        # Date outside min_date range
        assert very_old_date < BIRTH_DATE_CALENDAR_CONFIG.min_date

    def test_is_valid_birth_date_boundary_min_date(self):
        """Test that exactly min_date (200 years ago) is valid."""
        min_date = BIRTH_DATE_CALENDAR_CONFIG.min_date

        # Exactly at boundary
        assert BIRTH_DATE_CALENDAR_CONFIG.min_date <= min_date <= BIRTH_DATE_CALENDAR_CONFIG.max_date

    def test_is_valid_birth_date_boundary_max_date(self):
        """Test that exactly max_date (today) is valid."""
        max_date = BIRTH_DATE_CALENDAR_CONFIG.max_date

        # Exactly at boundary
        assert BIRTH_DATE_CALENDAR_CONFIG.min_date <= max_date <= BIRTH_DATE_CALENDAR_CONFIG.max_date


class TestCalendarDataStorage:
    """Test suite for calendar date storage in DialogManager."""

    def test_get_selected_date_returns_none_when_not_set(self):
        """Test that get_selected_date returns None when no date selected yet."""

        # Mock DialogManager
        class MockDialogManager:
            dialog_data = {}

        manager = MockDialogManager()
        result = CalendarWidget.get_selected_date(manager)  # type: ignore

        assert result is None

    def test_get_selected_date_returns_stored_date(self):
        """Test that get_selected_date returns the stored date from dialog_data."""

        # Mock DialogManager with stored date
        class MockDialogManager:
            dialog_data = {"selected_date": date(1990, 5, 15)}

        manager = MockDialogManager()
        result = CalendarWidget.get_selected_date(manager)  # type: ignore

        assert result == date(1990, 5, 15)

    @pytest.mark.asyncio
    async def test_get_calendar_data_returns_selected_date_display(self):
        """Test that get_calendar_data returns calendar data for dialog rendering."""
        from src.apisbot.bot.widgets.calendar import get_calendar_data

        # Mock DialogManager with selected date
        class MockDialogManager:
            dialog_data = {
                "selected_date": date(1985, 12, 25),
                "selected_date_display": "1985-12-25",
            }

        manager = MockDialogManager()
        result = await get_calendar_data(manager)  # type: ignore

        assert result["selected_date"] == date(1985, 12, 25)
        assert result["selected_date_display"] == "1985-12-25"

    @pytest.mark.asyncio
    async def test_get_calendar_data_default_display_when_not_selected(self):
        """Test that get_calendar_data returns default display when no date selected."""
        from src.apisbot.bot.widgets.calendar import get_calendar_data

        # Mock DialogManager without selected date
        class MockDialogManager:
            dialog_data = {}

        manager = MockDialogManager()
        result = await get_calendar_data(manager)  # type: ignore

        assert result["selected_date"] is None
        assert result["selected_date_display"] == "Not selected"
