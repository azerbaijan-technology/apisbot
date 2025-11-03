import logging

from kerykeion import AstrologicalSubject, AstrologicalSubjectFactory, ChartDataFactory, ChartDrawer

from ..models import BirthData

logger = logging.getLogger(__name__)


class ChartService:
    """Service for generating natal charts using kerykeion.

    This is a thin wrapper around kerykeion's AstrologicalSubject that:
    - Handles geocoding internally via kerykeion
    - Manages timezone determination via kerykeion
    - Provides error handling and logging
    - Generates SVG charts
    """

    @staticmethod
    async def generate_chart(birth_data: BirthData) -> str:
        """Generate natal chart SVG from birth data.

        Args:
            birth_data: User's birth information

        Returns:
            SVG chart as string

        Raises:
            ValueError: If location cannot be geocoded or chart generation fails
        """
        try:
            logger.info("Generating natal chart (no PII logged)")

            # Create astrological subject
            # Kerykeion handles geocoding and timezone determination internally
            subject = AstrologicalSubjectFactory.from_birth_data(
                name=birth_data.name,
                year=birth_data.birth_date.year,
                month=birth_data.birth_date.month,
                day=birth_data.birth_date.day,
                hour=birth_data.birth_time.hour,
                minute=birth_data.birth_time.minute,
                city=birth_data.location,
            )

            # Update birth_data with geocoded information (for debugging/logging)
            birth_data.latitude = subject.lat
            birth_data.longitude = subject.lng
            birth_data.timezone = subject.tz_str

            logger.info(f"Geocoding successful, timezone: {subject.tz_str}")

            chart_data = ChartDataFactory.create_natal_chart_data(subject)

            # Generate SVG chart
            drawer = ChartDrawer(chart_data)
            svg_chart = drawer.generate_wheel_only_svg_string(minify=True, remove_css_variables=True)

            logger.info("Chart generation successful")
            return svg_chart

        except Exception as e:
            logger.error(f"Chart generation failed: {type(e).__name__}: {str(e)}")

            # Provide user-friendly error messages
            if "city" in str(e).lower() or "location" in str(e).lower():
                raise ValueError(
                    f"Could not find location '{birth_data.location}'. "
                    "Please try a more specific location (e.g., 'New York, USA' instead of 'NYC')"
                ) from e

            raise ValueError(f"Failed to generate chart: {str(e)}") from e

    @staticmethod
    async def validate_location(location: str) -> tuple[float, float, str] | None:
        """Validate and geocode a location using kerykeion.

        Args:
            location: City name or location string

        Returns:
            Tuple of (latitude, longitude, timezone) if successful, None if not found
        """
        try:
            # Create a temporary subject to test geocoding
            # Use a dummy date since we only care about location
            subject = AstrologicalSubject(
                name="Test",
                year=2000,
                month=1,
                day=1,
                hour=12,
                minute=0,
                city=location,
            )

            if subject.lat and subject.lng:
                return (subject.lat, subject.lng, subject.tz_str)

            return None

        except Exception as e:
            logger.warning(f"Location validation failed for '{location}': {str(e)}")
            return None
