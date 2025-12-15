"""Input validation service coordinating all validation services.

Framework-agnostic service delegating to specialized validation services.
Returns ValidationError with remediation guidance per FR-005.
"""

from ..models.date_time import DateTimeData
from ..models.errors import ValidationError
from ..models.location import LocationData
from .date_time_service import DateTimeService
from .location_service import LocationService


class InputValidationService:
    """Unified input validation service coordinating specialized validators.

    Implements FR-005: ValidationError includes field_name and remediation_guidance.
    Implements FR-006: Never clear valid data on subsequent field validation failure.

    Delegates to:
    - DateTimeService for date/time validation
    - LocationService for location geocoding

    No aiogram dependencies: Fully testable without bot infrastructure.
    """

    @staticmethod
    async def validate_date(date_input: str) -> DateTimeData | ValidationError:
        """Validate date input by delegating to DateTimeService.

        Args:
            date_input: User's date input string

        Returns:
            DateTimeData if valid, ValidationError with remediation if invalid
        """
        return await DateTimeService.validate_date(date_input)

    @staticmethod
    async def validate_time(time_input: str) -> DateTimeData | ValidationError:
        """Validate time input by delegating to DateTimeService.

        Args:
            time_input: User's time input string

        Returns:
            DateTimeData with birth_time if valid, ValidationError if invalid
        """
        return await DateTimeService.validate_time(time_input)

    @staticmethod
    async def validate_location(location_input: str) -> LocationData | ValidationError:
        """Validate location input by delegating to LocationService.

        Args:
            location_input: User's location input string (city name)

        Returns:
            LocationData if geocoding successful, ValidationError with recovery options if failed
        """
        return await LocationService.geocode_location(location_input)

    @staticmethod
    def validate_name(name_input: str) -> str | ValidationError:
        """Validate name input (1-100 characters with at least one letter).

        Args:
            name_input: User's name input

        Returns:
            Validated name string if valid, ValidationError if invalid
        """
        name = name_input.strip()

        # Check length
        if not name or len(name) < 1:
            return ValidationError(
                field_name="name",
                message="Name cannot be empty",
                remediation="Please enter a name (1-100 characters with at least one letter).\n" "Example: John Doe",
                user_input=name_input,
            )

        if len(name) > 100:
            return ValidationError(
                field_name="name",
                message=f"Name is too long ({len(name)} characters)",
                remediation="Please enter a name with 100 characters or less.",
                user_input=name_input,
            )

        # Check contains at least one letter
        if not any(c.isalpha() for c in name):
            return ValidationError(
                field_name="name",
                message="Name must contain at least one letter",
                remediation="Please enter a valid name with at least one letter.\n" "Example: John Doe, María, 李明",
                user_input=name_input,
            )

        return name
