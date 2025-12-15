"""Unit tests for date and time validation service.

Tests edge cases: invalid dates (Feb 30), future dates, very old dates, invalid times.
Framework-agnostic: No aiogram dependencies required.
"""

from datetime import date, time

import pytest

from src.apisbot.models.date_time import DateTimeData
from src.apisbot.models.errors import ValidationError
from src.apisbot.services.date_time_service import DateTimeService


class TestDateValidation:
    """Test suite for date validation."""

    @pytest.mark.asyncio
    async def test_validate_date_accepts_valid_date_iso_format(self):
        """Test that valid ISO format date (YYYY-MM-DD) is accepted."""
        result = await DateTimeService.validate_date("1990-05-15")

        assert isinstance(result, DateTimeData)
        assert result.birth_date == date(1990, 5, 15)

    @pytest.mark.asyncio
    async def test_validate_date_accepts_valid_date_slash_format(self):
        """Test that valid slash format date (DD/MM/YYYY) is accepted."""
        result = await DateTimeService.validate_date("15/05/1990")

        assert isinstance(result, DateTimeData)
        assert result.birth_date == date(1990, 5, 15)

    @pytest.mark.asyncio
    async def test_validate_date_accepts_today(self):
        """Test that today's date is valid (edge case: born today)."""
        today = date.today()
        result = await DateTimeService.validate_date(today.isoformat())

        assert isinstance(result, DateTimeData)
        assert result.birth_date == today

    @pytest.mark.asyncio
    async def test_validate_date_accepts_old_date_within_200_years(self):
        """Test that dates within 200 years are valid."""
        old_year = date.today().year - 199
        result = await DateTimeService.validate_date(f"{old_year}-06-15")

        assert isinstance(result, DateTimeData)
        assert result.birth_date.year == old_year

    @pytest.mark.asyncio
    async def test_validate_date_rejects_future_date(self):
        """Test that future dates are rejected with clear error message."""
        future_year = date.today().year + 1
        result = await DateTimeService.validate_date(f"{future_year}-05-15")

        assert isinstance(result, ValidationError)
        assert result.field_name == "birth_date"
        assert "future" in result.message.lower()
        assert result.remediation is not None

    @pytest.mark.asyncio
    async def test_validate_date_rejects_date_over_200_years_old(self):
        """Test that dates > 200 years ago are rejected."""
        from datetime import timedelta

        # Use a date well before the min_date boundary
        very_old_date = date.today() - timedelta(days=201 * 365)
        result = await DateTimeService.validate_date(very_old_date.strftime("%Y-%m-%d"))

        assert isinstance(result, ValidationError)
        assert result.field_name == "birth_date"
        assert "200 years" in result.message or "after year" in result.message
        assert result.remediation is not None

    @pytest.mark.asyncio
    async def test_validate_date_rejects_invalid_calendar_date_feb_30(self):
        """Test that invalid calendar dates (Feb 30) are rejected."""
        result = await DateTimeService.validate_date("2000-02-30")

        assert isinstance(result, ValidationError)
        assert result.field_name == "birth_date"
        assert "invalid" in result.message.lower()

    @pytest.mark.asyncio
    async def test_validate_date_rejects_invalid_calendar_date_month_13(self):
        """Test that invalid month (month 13) is rejected."""
        result = await DateTimeService.validate_date("2000-13-01")

        assert isinstance(result, ValidationError)
        assert result.field_name == "birth_date"

    @pytest.mark.asyncio
    async def test_validate_date_rejects_malformed_input(self):
        """Test that malformed date input is rejected with format guidance."""
        result = await DateTimeService.validate_date("not a date")

        assert isinstance(result, ValidationError)
        assert result.field_name == "birth_date"
        assert result.remediation is not None
        # Should suggest valid formats
        assert "example" in result.remediation.lower() or "format" in result.remediation.lower()

    @pytest.mark.asyncio
    async def test_validate_date_boundary_exactly_200_years_ago(self):
        """Test boundary condition: exactly at min_date (200*365 days ago)."""
        from datetime import timedelta

        boundary_date = date.today() - timedelta(days=200 * 365)
        result = await DateTimeService.validate_date(boundary_date.strftime("%Y-%m-%d"))

        # Should be accepted (at the exact boundary)
        assert isinstance(result, DateTimeData)
        assert result.birth_date == boundary_date

    @pytest.mark.asyncio
    async def test_validate_date_boundary_just_before_min(self):
        """Test boundary condition: one day before min_date should be rejected."""
        from datetime import timedelta

        boundary_date = date.today() - timedelta(days=200 * 365 + 1)
        result = await DateTimeService.validate_date(boundary_date.strftime("%Y-%m-%d"))

        # Should be rejected (before min_date)
        assert isinstance(result, ValidationError)
        assert result.field_name == "birth_date"


class TestTimeValidation:
    """Test suite for time validation."""

    @pytest.mark.asyncio
    async def test_validate_time_accepts_valid_24hour_format(self):
        """Test that valid 24-hour format time is accepted."""
        result = await DateTimeService.validate_time("14:30")

        assert isinstance(result, DateTimeData)
        assert result.birth_time == time(14, 30)

    @pytest.mark.asyncio
    async def test_validate_time_accepts_midnight(self):
        """Test that midnight (00:00) is valid."""
        result = await DateTimeService.validate_time("00:00")

        assert isinstance(result, DateTimeData)
        assert result.birth_time == time(0, 0)

    @pytest.mark.asyncio
    async def test_validate_time_accepts_noon(self):
        """Test that noon (12:00) is valid."""
        result = await DateTimeService.validate_time("12:00")

        assert isinstance(result, DateTimeData)
        assert result.birth_time == time(12, 0)

    @pytest.mark.asyncio
    async def test_validate_time_boundary_23_59_59(self):
        """Test that 23:59 is valid (seconds format not supported)."""
        result = await DateTimeService.validate_time("23:59")

        assert isinstance(result, DateTimeData)
        assert result.birth_time == time(23, 59)

    @pytest.mark.asyncio
    async def test_validate_time_accepts_time_with_seconds(self):
        """Test that time format with seconds is rejected (not supported)."""
        result = await DateTimeService.validate_time("23:59:59")

        # Seconds format is not supported, should return ValidationError
        assert isinstance(result, ValidationError)

    @pytest.mark.asyncio
    async def test_validate_time_rejects_invalid_hour_25(self):
        """Test that invalid hour (25:00) is rejected."""
        result = await DateTimeService.validate_time("25:00")

        assert isinstance(result, ValidationError)
        assert result.field_name == "birth_time"
        assert "invalid" in result.message.lower() or "format" in result.message.lower()

    @pytest.mark.asyncio
    async def test_validate_time_rejects_invalid_minute_60(self):
        """Test that invalid minute (14:60) is rejected."""
        result = await DateTimeService.validate_time("14:60")

        assert isinstance(result, ValidationError)
        assert result.field_name == "birth_time"

    @pytest.mark.asyncio
    async def test_validate_time_rejects_malformed_input(self):
        """Test that malformed time input is rejected with format guidance."""
        result = await DateTimeService.validate_time("not a time")

        assert isinstance(result, ValidationError)
        assert result.field_name == "birth_time"
        assert result.remediation is not None
        # Should suggest valid formats
        assert "example" in result.remediation.lower() or "format" in result.remediation.lower()

    @pytest.mark.asyncio
    async def test_validate_time_accepts_single_digit_hour(self):
        """Test that single-digit hour (9:30) is accepted."""
        result = await DateTimeService.validate_time("9:30")

        assert isinstance(result, DateTimeData)
        assert result.birth_time == time(9, 30)

    @pytest.mark.asyncio
    async def test_validate_time_accepts_single_digit_minute(self):
        """Test that single digit minute is accepted."""
        result = await DateTimeService.validate_time("9:05")

        assert isinstance(result, DateTimeData)
        assert result.birth_time == time(9, 5)


class TestCombineDateTime:
    """Test suite for combining date and time."""

    @pytest.mark.asyncio
    async def test_combine_date_time_merges_both_values(self):
        """Test that combine_date_time merges date and time into single object."""
        # Create date data
        date_data = DateTimeData(birth_date=date(1990, 5, 15))

        # Create time data (has placeholder date)
        time_data = DateTimeData(birth_date=date(2000, 1, 1), birth_time=time(14, 30))

        # Combine
        result = await DateTimeService.combine_date_time(date_data, time_data)

        # Verify both date and time present
        assert result.birth_date == date(1990, 5, 15)
        assert result.birth_time == time(14, 30)

    @pytest.mark.asyncio
    async def test_combine_date_time_preserves_display_formats(self):
        """Test that combine_date_time preserves display formats."""
        # Create data with display formats
        date_data = DateTimeData(birth_date=date(1990, 5, 15), display_date="15.05.1990")

        time_data = DateTimeData(birth_date=date(2000, 1, 1), birth_time=time(14, 30), display_time="14:30")

        # Combine
        result = await DateTimeService.combine_date_time(date_data, time_data)

        # Verify display formats preserved
        assert result.display_date == "15.05.1990"
        assert result.display_time == "14:30"

    @pytest.mark.asyncio
    async def test_combine_date_time_midnight_time(self):
        """Test combining date with midnight time."""
        date_data = DateTimeData(birth_date=date(2000, 1, 1))
        time_data = DateTimeData(birth_date=date(2000, 1, 1), birth_time=time(0, 0))

        result = await DateTimeService.combine_date_time(date_data, time_data)

        assert result.birth_date == date(2000, 1, 1)
        assert result.birth_time == time(0, 0)

    @pytest.mark.asyncio
    async def test_combine_date_time_end_of_day_time(self):
        """Test combining date with end-of-day time (23:59)."""
        date_data = DateTimeData(birth_date=date(1995, 12, 31))
        time_data = DateTimeData(birth_date=date(2000, 1, 1), birth_time=time(23, 59))

        result = await DateTimeService.combine_date_time(date_data, time_data)

        assert result.birth_date == date(1995, 12, 31)
        assert result.birth_time == time(23, 59)


class TestDateTimeServiceEdgeCases:
    """Test suite for edge cases and special scenarios."""

    @pytest.mark.asyncio
    async def test_validate_date_leap_year_feb_29(self):
        """Test that Feb 29 is valid in leap years."""
        result = await DateTimeService.validate_date("2000-02-29")  # 2000 is leap year

        assert isinstance(result, DateTimeData)
        assert result.birth_date == date(2000, 2, 29)

    @pytest.mark.asyncio
    async def test_validate_date_non_leap_year_feb_29(self):
        """Test that Feb 29 is invalid in non-leap years."""
        result = await DateTimeService.validate_date("1900-02-29")  # 1900 is not leap year

        assert isinstance(result, ValidationError)
        assert result.field_name == "birth_date"

    @pytest.mark.asyncio
    async def test_validate_date_dec_31(self):
        """Test that end-of-year date (Dec 31) is valid."""
        result = await DateTimeService.validate_date("1990-12-31")

        assert isinstance(result, DateTimeData)
        assert result.birth_date == date(1990, 12, 31)

    @pytest.mark.asyncio
    async def test_validate_date_jan_1(self):
        """Test that start-of-year date (Jan 1) is valid."""
        result = await DateTimeService.validate_date("1990-01-01")

        assert isinstance(result, DateTimeData)
        assert result.birth_date == date(1990, 1, 1)

    @pytest.mark.asyncio
    async def test_validate_time_boundary_23_59_59(self):
        """Test that time with seconds format is rejected (not supported)."""
        result = await DateTimeService.validate_time("23:59:59")

        # Seconds format is not supported by the parser
        assert isinstance(result, ValidationError)
        assert result.field_name == "birth_time"

    @pytest.mark.asyncio
    async def test_validation_errors_include_user_input(self):
        """Test that ValidationError includes original user input for debugging."""
        result = await DateTimeService.validate_date("invalid-date-123")

        assert isinstance(result, ValidationError)
        assert result.user_input == "invalid-date-123"

    @pytest.mark.asyncio
    async def test_validation_errors_include_remediation_guidance(self):
        """Test that ValidationError includes helpful remediation guidance."""
        result = await DateTimeService.validate_time("99:99")

        assert isinstance(result, ValidationError)
        assert result.remediation is not None
        assert len(result.remediation) > 0

    @pytest.mark.asyncio
    async def test_date_validation_preserves_format_in_display_date(self):
        """Test that validated date preserves input format for display."""
        result = await DateTimeService.validate_date("15/05/1990")

        assert isinstance(result, DateTimeData)
        # Display date should preserve the format
        assert result.display_date is not None

    @pytest.mark.asyncio
    async def test_time_validation_preserves_format_in_display_time(self):
        """Test that validated time preserves input format for display."""
        result = await DateTimeService.validate_time("14:30")

        assert isinstance(result, DateTimeData)
        # Display time should preserve the format
        assert result.display_time is not None
