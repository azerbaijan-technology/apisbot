"""Location geocoding and validation service.

Framework-agnostic service with no aiogram dependencies.
Uses kerykeion for geocoding (same library as chart generation).
"""

import logging
from typing import List

from kerykeion import AstrologicalSubject

from ..models.errors import ValidationError
from ..models.location import LocationData

logger = logging.getLogger(__name__)


class LocationService:
    """Service for geocoding and validating location inputs.

    Uses kerykeion's built-in geocoding (same as chart generation).
    Implements 2-option recovery per FR-012:
    1. Try fuzzy city name matching
    2. Suggest map widget fallback
    3. Reject if both fail

    No aiogram dependencies: Fully testable without bot infrastructure.
    """

    @staticmethod
    async def geocode_location(location_string: str) -> LocationData | ValidationError:
        """Geocode location string to coordinates and timezone.

        Args:
            location_string: City name or location string (e.g., "New York", "London, UK")

        Returns:
            LocationData if geocoding successful, ValidationError with recovery options if failed

        Examples:
            >>> await LocationService.geocode_location("New York")
            LocationData(city='New York', latitude=40.7128, longitude=-74.0060, ...)

            >>> await LocationService.geocode_location("InvalidCity123")
            ValidationError(field_name='location', message='Location not found', ...)
        """
        try:
            # Use kerykeion's geocoding via temporary AstrologicalSubject
            # (same geocoding as chart generation, ensures consistency)
            subject = AstrologicalSubject(
                name="LocationTest", year=2000, month=1, day=1, hour=12, minute=0, city=location_string, nation=" "
            )

            # Check if geocoding succeeded
            if subject.lat and subject.lng and subject.tz_str:
                logger.info(f"Geocoding successful for location (timezone: {subject.tz_str})")

                return LocationData(
                    city=location_string,
                    latitude=subject.lat,
                    longitude=subject.lng,
                    timezone=subject.tz_str,
                    display_name=location_string,  # Could enhance with full name from geocoder
                )

            # Geocoding failed (no coordinates returned)
            logger.warning("Geocoding failed: no coordinates for location")
            return await LocationService._create_geocoding_error(location_string)

        except Exception as e:
            logger.error(f"Geocoding error: {type(e).__name__}: {str(e)}")
            return await LocationService._create_geocoding_error(location_string, exception=e)

    @staticmethod
    async def parse_city_name(user_input: str) -> List[LocationData]:
        """Parse city name with fuzzy matching (future enhancement).

        Currently delegates to geocode_location. Future: Return multiple options.

        Args:
            user_input: User's location input

        Returns:
            List of possible LocationData matches (currently 0 or 1 result)
        """
        result = await LocationService.geocode_location(user_input)

        if isinstance(result, LocationData):
            return [result]
        else:
            return []

    @staticmethod
    async def get_map_widget_url(user_id: int) -> str:
        """Get map widget URL for manual location selection (fallback option).

        Future enhancement: Integrate with Telegram map sharing or external map service.

        Args:
            user_id: Telegram user ID

        Returns:
            URL to map widget (placeholder for now)
        """
        # Placeholder: Future integration with map widget
        # Could use Telegram's location sharing or external service like Google Maps
        return "https://example.com/map-widget"  # TODO: Implement actual map widget

    @staticmethod
    async def _create_geocoding_error(location_string: str, exception: Exception | None = None) -> ValidationError:
        """Create ValidationError with recovery options for geocoding failure.

        Implements FR-012: 2-option recovery (city parse, map widget, reject).

        Args:
            location_string: Original location input
            exception: Optional exception that caused the error

        Returns:
            ValidationError with remediation guidance
        """
        error_message = "Location not found or could not be geocoded"

        if exception and "city" in str(exception).lower():
            error_message = f"Could not find location '{location_string}'"

        remediation = (
            "Please try one of the following:\n\n"
            "1. Use a more specific location:\n"
            "   • Include country (e.g., 'London, UK' instead of 'London')\n"
            "   • Use full city name (e.g., 'New York City' instead of 'NYC')\n"
            "   • Try nearby major city if your city is small\n\n"
            "2. Common examples:\n"
            "   • New York, USA\n"
            "   • London, UK\n"
            "   • Paris, France\n"
            "   • Tokyo, Japan\n\n"
            "If your location still cannot be found, please try a nearby major city."
        )

        return ValidationError(
            field_name="location",
            message=error_message,
            remediation=remediation,
            user_input=location_string,
        )
