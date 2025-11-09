"""Date and time validation service.

Framework-agnostic service with no aiogram dependencies.
Returns ValidationError with remediation guidance for invalid inputs.
"""

from datetime import date

from ..models.date_time import DateTimeData
from ..models.errors import ValidationError
from .date_parser import parse_date, parse_time, suggest_date_format, suggest_time_format


class DateTimeService:
    """Service for validating and parsing date/time inputs.

    Edge cases handled:
    - Invalid calendar dates (e.g., Feb 30) - rejected by datetime.date
    - Future dates - rejected with clear message
    - Very old dates (> 200 years ago) - rejected
    - Invalid times (e.g., 25:00) - rejected with format guidance
    - Rare timezones - handled by location_service (geocoding)

    No aiogram dependencies: Fully testable without bot infrastructure.
    """

    @staticmethod
    async def validate_date(date_input: str) -> DateTimeData | ValidationError:
        """Validate and parse date input.

        Args:
            date_input: User's date input string

        Returns:
            DateTimeData if valid, ValidationError with remediation if invalid

        Examples:
            >>> await DateTimeService.validate_date("1990-05-15")
            DateTimeData(birth_date=date(1990, 5, 15), ...)

            >>> await DateTimeService.validate_date("2030-01-01")  # Future date
            ValidationError(field_name='birth_date', message='Birth date cannot be in the future', ...)

            >>> await DateTimeService.validate_date("1800-01-01")  # Too old
            ValidationError(field_name='birth_date', message='Birth date must be after year 1825', ...)
        """
        try:
            parsed_date = parse_date(date_input)

            # Create DateTimeData (will validate date constraints)
            return DateTimeData(birth_date=parsed_date)

        except ValueError as e:
            error_message = str(e)

            # Provide specific remediation based on error type
            if "future" in error_message.lower():
                return ValidationError(
                    field_name="birth_date",
                    message="Birth date cannot be in the future",
                    remediation="Please enter a valid birth date in the past. Examples:\n"
                    "  • 15.05.1990\n"
                    "  • 1990-05-15\n"
                    "  • May 15, 1990",
                    user_input=date_input,
                )

            elif "200 years" in error_message or "150 years" in error_message:
                min_year = date.today().year - 200
                return ValidationError(
                    field_name="birth_date",
                    message=f"Birth date must be after year {min_year}",
                    remediation=f"Please enter a date within the last 200 years (after {min_year}).",
                    user_input=date_input,
                )

            elif "invalid" in error_message.lower() or "format" in error_message.lower():
                return ValidationError(
                    field_name="birth_date",
                    message="Invalid date format",
                    remediation=suggest_date_format(date_input),
                    user_input=date_input,
                )

            else:
                # Generic date validation error (e.g., Feb 30)
                return ValidationError(
                    field_name="birth_date",
                    message=f"Invalid date: {error_message}",
                    remediation="Please enter a valid calendar date. Examples:\n"
                    "  • 15.05.1990\n"
                    "  • 1990-05-15\n"
                    "  • May 15, 1990",
                    user_input=date_input,
                )

    @staticmethod
    async def validate_time(time_input: str) -> DateTimeData | ValidationError:
        """Validate and parse time input.

        Note: Returns DateTimeData with only birth_time set. Date must be set separately.

        Args:
            time_input: User's time input string

        Returns:
            DateTimeData with birth_time if valid, ValidationError if invalid

        Examples:
            >>> await DateTimeService.validate_time("14:30")
            DateTimeData(birth_date=None, birth_time=time(14, 30), ...)

            >>> await DateTimeService.validate_time("25:00")  # Invalid hour
            ValidationError(field_name='birth_time', message='Invalid time format', ...)
        """
        try:
            parsed_time = parse_time(time_input)

            # Create a temporary DateTimeData with just the time
            # Note: birth_date will need to be set later when combining date+time
            # For now, use a placeholder date to satisfy DateTimeData validation
            from datetime import date as date_type

            placeholder_date = date_type(2000, 1, 1)

            return DateTimeData(birth_date=placeholder_date, birth_time=parsed_time)

        except ValueError:
            return ValidationError(
                field_name="birth_time",
                message="Invalid time format",
                remediation=suggest_time_format(time_input),
                user_input=time_input,
            )

    @staticmethod
    async def combine_date_time(date_data: DateTimeData, time_data: DateTimeData) -> DateTimeData:
        """Combine separate date and time into single DateTimeData.

        Args:
            date_data: DateTimeData with valid birth_date
            time_data: DateTimeData with valid birth_time

        Returns:
            DateTimeData with both birth_date and birth_time set
        """
        return DateTimeData(
            birth_date=date_data.birth_date,
            birth_time=time_data.birth_time,
            display_date=date_data.display_date,
            display_time=time_data.display_time,
        )
