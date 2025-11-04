"""Tests for date_parser service."""

from datetime import date, time, timedelta

import pytest

from apisbot.services.date_parser import (
    parse_date,
    parse_time,
    suggest_date_format,
    suggest_time_format,
)


class TestParseDate:
    """Test date parsing functionality."""

    def test_parse_date_yyyy_mm_dd(self):
        """Test YYYY-MM-DD format."""
        assert parse_date("1990-05-15") == date(1990, 5, 15)
        assert parse_date("2000-01-01") == date(2000, 1, 1)
        assert parse_date("1985-12-31") == date(1985, 12, 31)

    def test_parse_date_dd_mm_yyyy_slash(self):
        """Test DD/MM/YYYY format."""
        assert parse_date("15/05/1990") == date(1990, 5, 15)
        assert parse_date("01/01/2000") == date(2000, 1, 1)
        assert parse_date("31/12/1985") == date(1985, 12, 31)

    def test_parse_date_dd_mm_yyyy_dash(self):
        """Test DD-MM-YYYY format."""
        assert parse_date("15-05-1990") == date(1990, 5, 15)
        assert parse_date("01-01-2000") == date(2000, 1, 1)
        assert parse_date("31-12-1985") == date(1985, 12, 31)

    def test_parse_date_month_dd_yyyy(self):
        """Test 'Month DD, YYYY' format."""
        assert parse_date("May 15, 1990") == date(1990, 5, 15)
        assert parse_date("January 1, 2000") == date(2000, 1, 1)
        assert parse_date("December 31 1985") == date(1985, 12, 31)  # Without comma

    def test_parse_date_dd_month_yyyy(self):
        """Test 'DD Month YYYY' format."""
        assert parse_date("15 May 1990") == date(1990, 5, 15)
        assert parse_date("1 January 2000") == date(2000, 1, 1)
        assert parse_date("31 December 1985") == date(1985, 12, 31)

    def test_parse_date_with_whitespace(self):
        """Test date parsing with extra whitespace."""
        assert parse_date("  1990-05-15  ") == date(1990, 5, 15)
        assert parse_date(" 15/05/1990 ") == date(1990, 5, 15)

    def test_parse_date_future_raises_error(self):
        """Test that future dates raise ValueError."""
        tomorrow = date.today() + timedelta(days=1)
        with pytest.raises(ValueError, match="cannot be in the future"):
            parse_date(tomorrow.strftime("%Y-%m-%d"))

    def test_parse_date_too_old_raises_error(self):
        """Test that dates older than 150 years raise ValueError."""
        too_old = date.today() - timedelta(days=151 * 365)
        with pytest.raises(ValueError, match="cannot be more than 150 years ago"):
            parse_date(too_old.strftime("%Y-%m-%d"))

    def test_parse_date_invalid_format(self):
        """Test that invalid formats raise ValueError."""
        invalid_dates = [
            "not a date",
            "1990/05/15",  # Wrong separators
            "15.05.1990",
            "1990",
            "May 1990",
            "32/01/1990",  # Invalid day
            "01/13/1990",  # Invalid month in DD/MM format
        ]

        for invalid_date in invalid_dates:
            with pytest.raises(ValueError):
                parse_date(invalid_date)


class TestParseTime:
    """Test time parsing functionality."""

    def test_parse_time_24h_format(self):
        """Test 24-hour HH:MM format."""
        assert parse_time("14:30") == time(14, 30)
        assert parse_time("00:00") == time(0, 0)
        assert parse_time("23:59") == time(23, 59)
        assert parse_time("9:05") == time(9, 5)

    def test_parse_time_hour_only_24h(self):
        """Test hour-only format (24-hour)."""
        assert parse_time("14") == time(14, 0)
        assert parse_time("0") == time(0, 0)
        assert parse_time("23") == time(23, 0)

    def test_parse_time_12h_format_am(self):
        """Test 12-hour format with AM."""
        assert parse_time("2:30 AM") == time(2, 30)
        assert parse_time("12:00 AM") == time(0, 0)  # Midnight
        assert parse_time("11:59 am") == time(11, 59)

    def test_parse_time_12h_format_pm(self):
        """Test 12-hour format with PM."""
        assert parse_time("2:30 PM") == time(14, 30)
        assert parse_time("12:00 PM") == time(12, 0)  # Noon
        assert parse_time("11:59 pm") == time(23, 59)

    def test_parse_time_hour_only_12h(self):
        """Test hour-only format with AM/PM."""
        assert parse_time("2 AM") == time(2, 0)
        assert parse_time("2 PM") == time(14, 0)
        assert parse_time("12 AM") == time(0, 0)
        assert parse_time("12 PM") == time(12, 0)

    def test_parse_time_with_whitespace(self):
        """Test time parsing with extra whitespace."""
        assert parse_time("  14:30  ") == time(14, 30)
        assert parse_time(" 2:30 PM ") == time(14, 30)

    def test_parse_time_invalid_24h_hour(self):
        """Test that invalid hours in 24h format raise ValueError."""
        with pytest.raises(ValueError, match="hours must be 0-23"):
            parse_time("24:00")
        with pytest.raises(ValueError, match="hours must be 0-23"):
            parse_time("25:30")

    def test_parse_time_invalid_24h_minute(self):
        """Test that invalid minutes raise ValueError."""
        with pytest.raises(ValueError, match="minutes must be 0-59"):
            parse_time("14:60")
        with pytest.raises(ValueError, match="minutes must be 0-59"):
            parse_time("14:99")

    def test_parse_time_invalid_12h_hour(self):
        """Test that invalid hours in 12h format raise ValueError."""
        with pytest.raises(ValueError, match="hours must be 1-12"):
            parse_time("0 AM")
        with pytest.raises(ValueError, match="hours must be 1-12"):
            parse_time("13 PM")

    def test_parse_time_invalid_format(self):
        """Test that invalid formats raise ValueError."""
        invalid_times = [
            "not a time",
            "14:30:45",  # Seconds not supported
        ]

        for invalid_time in invalid_times:
            with pytest.raises(ValueError):
                parse_time(invalid_time)

        # Test invalid hour separately
        with pytest.raises(ValueError):
            parse_time("25")


class TestSuggestDateFormat:
    """Test date format suggestion helper."""

    def test_suggest_date_format(self):
        """Test that suggestion includes the invalid input and examples."""
        suggestion = suggest_date_format("invalid")

        assert "invalid" in suggestion
        assert "YYYY-MM-DD" in suggestion
        assert "DD/MM/YYYY" in suggestion
        assert "1990-05-15" in suggestion


class TestSuggestTimeFormat:
    """Test time format suggestion helper."""

    def test_suggest_time_format(self):
        """Test that suggestion includes the invalid input and examples."""
        suggestion = suggest_time_format("invalid")

        assert "invalid" in suggestion
        assert "HH:MM" in suggestion
        assert "AM/PM" in suggestion
        assert "14:30" in suggestion
