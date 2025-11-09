"""Tests for DateTimeData model."""

from datetime import date, datetime, time

import pytest

from apisbot.models.date_time import DateTimeData


class TestDateTimeData:
    """Test DateTimeData model validation and functionality."""

    def test_date_time_data_creation(self):
        """Test basic DateTimeData instantiation."""
        dt_data = DateTimeData(
            birth_date=date(1990, 5, 15),
            birth_time=time(14, 30),
        )

        assert dt_data.birth_date == date(1990, 5, 15)
        assert dt_data.birth_time == time(14, 30)
        assert dt_data.display_date is not None
        assert dt_data.display_time is not None

    def test_date_time_data_without_time(self):
        """Test DateTimeData with date only (no time)."""
        dt_data = DateTimeData(birth_date=date(1990, 5, 15))

        assert dt_data.birth_date == date(1990, 5, 15)
        assert dt_data.birth_time is None
        assert dt_data.display_date is not None
        assert dt_data.display_time is None

    def test_date_time_data_with_custom_display_formats(self):
        """Test DateTimeData with custom display formats."""
        dt_data = DateTimeData(
            birth_date=date(1990, 5, 15),
            birth_time=time(14, 30),
            display_date="15/05/1990",
            display_time="2:30 PM",
        )

        assert dt_data.display_date == "15/05/1990"
        assert dt_data.display_time == "2:30 PM"

    def test_date_time_data_auto_display_date_format(self):
        """Test that display_date is auto-generated in DD.MM.YYYY format."""
        dt_data = DateTimeData(birth_date=date(1990, 5, 15))

        assert dt_data.display_date == "15.05.1990"

    def test_date_time_data_auto_display_time_format(self):
        """Test that display_time is auto-generated in HH:MM format."""
        dt_data = DateTimeData(
            birth_date=date(1990, 5, 15),
            birth_time=time(14, 30),
        )

        assert dt_data.display_time == "14:30"

    def test_date_time_data_validates_future_date(self):
        """Test that future dates are rejected."""
        from datetime import timedelta

        future_date = date.today() + timedelta(days=1)

        with pytest.raises(ValueError, match="cannot be in the future"):
            DateTimeData(birth_date=future_date)

    def test_date_time_data_validates_very_old_date(self):
        """Test that dates > 200 years ago are rejected."""
        old_year = date.today().year - 201
        old_date = date(old_year, 1, 1)

        with pytest.raises(ValueError, match="must be after year"):
            DateTimeData(birth_date=old_date)

    def test_date_time_data_accepts_today(self):
        """Test that today's date is accepted."""
        today = date.today()
        dt_data = DateTimeData(birth_date=today)

        assert dt_data.birth_date == today

    def test_date_time_data_accepts_date_200_years_ago(self):
        """Test that date exactly 200 years ago is accepted."""
        boundary_year = date.today().year - 200
        boundary_date = date(boundary_year, 1, 1)

        dt_data = DateTimeData(birth_date=boundary_date)

        assert dt_data.birth_date == boundary_date

    def test_datetime_property_with_time(self):
        """Test datetime property returns combined datetime."""
        dt_data = DateTimeData(
            birth_date=date(1990, 5, 15),
            birth_time=time(14, 30),
        )

        dt = dt_data.datetime

        assert dt is not None
        assert isinstance(dt, datetime)
        assert dt.year == 1990
        assert dt.month == 5
        assert dt.day == 15
        assert dt.hour == 14
        assert dt.minute == 30

    def test_datetime_property_without_time(self):
        """Test datetime property returns None when time is not set."""
        dt_data = DateTimeData(birth_date=date(1990, 5, 15))

        assert dt_data.datetime is None

    def test_datetime_property_with_midnight(self):
        """Test datetime property with midnight time."""
        dt_data = DateTimeData(
            birth_date=date(1990, 5, 15),
            birth_time=time(0, 0),
        )

        dt = dt_data.datetime

        assert dt is not None
        assert dt.hour == 0
        assert dt.minute == 0

    def test_datetime_property_with_end_of_day(self):
        """Test datetime property with end of day time."""
        dt_data = DateTimeData(
            birth_date=date(1990, 5, 15),
            birth_time=time(23, 59),
        )

        dt = dt_data.datetime

        assert dt is not None
        assert dt.hour == 23
        assert dt.minute == 59
