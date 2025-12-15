"""Chart generation service for natal and composite charts.

Framework-agnostic service with async/await for all I/O operations.
No aiogram dependencies - fully testable without bot infrastructure.
"""

import logging
from typing import List

import kerykeion.composite_subject_factory
from kerykeion import (
    AstrologicalSubject,
    AstrologicalSubjectFactory,
    ChartDataFactory,
    CompositeSubjectFactory,
    ReportGenerator,
)
from kerykeion.schemas import ActiveAspect, AstrologicalPoint
from kerykeion.utilities import AstrologicalSubjectModel

from ..models import BirthData
from ..models.chart_selection import ChartSelection

logger = logging.getLogger(__name__)

_original_circular_mean = kerykeion.composite_subject_factory.circular_mean


def _patched_circular_mean(p1, p2):

    result = _original_circular_mean(p1, p2)
    return result % 360


kerykeion.composite_subject_factory.circular_mean = _patched_circular_mean


class ChartService:
    """Service for generating natal and composite charts using kerykeion.

    Refactored to support both chart types with common logic extraction.
    Framework-agnostic: No aiogram dependencies, async/await for all I/O.

    Features:
    - Handles geocoding internally via kerykeion
    - Manages timezone determination via kerykeion
    - Provides error handling and logging
    - Generates SVG charts for both Natal and Composite types
    - Privacy-first: No PII logged
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
                nation=birth_data.nation,
                houses_system_identifier="W",
            )

            # Update birth_data with geocoded information (for debugging/logging)
            birth_data.latitude = subject.lat
            birth_data.longitude = subject.lng
            birth_data.timezone = subject.tz_str

            logger.info(f"Geocoding successful, timezone: {subject.tz_str}")

            active_points: List[AstrologicalPoint] = [
                "Sun",
                "Moon",
                "Mercury",
                "Venus",
                "Mars",
                "Jupiter",
                "Saturn",
                "Uranus",
                "Neptune",
                "Pluto",
            ]
            active_aspects: List[ActiveAspect] = [
                {"name": "conjunction", "orb": 5},
                {"name": "opposition", "orb": 5},
                {"name": "trine", "orb": 5},
                {"name": "square", "orb": 5},
                {"name": "sextile", "orb": 3},
            ]

            chart_data = CustomChartDataFactory.create_natal_chart_data(
                subject, active_points=active_points, active_aspects=active_aspects, restrict_to_similar_signs=True
            )

            # Generate SVG chart
            drawer = CustomChartDrawer(chart_data=chart_data, theme="my-theme")
            svg_chart = drawer.generate_wheel_only_svg_string(minify=True, remove_css_variables=True)

            logger.info("Natal chart generation successful")
            return svg_chart

        except Exception as e:
            logger.error(f"Natal chart generation failed: {type(e).__name__}: {str(e)}")

            # Provide user-friendly error messages
            if "city" in str(e).lower() or "location" in str(e).lower():
                raise ValueError(
                    f"Could not find location '{birth_data.location}'. "
                    "Please try a more specific location (e.g., 'New York, USA' instead of 'NYC')"
                ) from e

            raise ValueError(f"Failed to generate natal chart: {str(e)}") from e

    @staticmethod
    async def generate_composite(birth_data_1: BirthData, birth_data_2: BirthData) -> str:
        try:
            logger.info("Generating composite chart (no PII logged)")

            # Create astrological subjects (geonames lookup happens here)
            try:
                subject_1 = AstrologicalSubjectFactory.from_birth_data(
                    name=birth_data_1.name,
                    year=birth_data_1.birth_date.year,
                    month=birth_data_1.birth_date.month,
                    day=birth_data_1.birth_date.day,
                    hour=birth_data_1.birth_time.hour,
                    minute=birth_data_1.birth_time.minute,
                    city=birth_data_1.location,
                    nation=birth_data_1.nation,
                    houses_system_identifier="W",
                )
                # Update birth_data with geocoded info
                birth_data_1.latitude = subject_1.lat
                birth_data_1.longitude = subject_1.lng
                birth_data_1.timezone = subject_1.tz_str
            except Exception as e:
                raise ValueError(f"Could not find location for first person: {birth_data_1.location}") from e

            try:
                subject_2 = AstrologicalSubjectFactory.from_birth_data(
                    name=birth_data_2.name,
                    year=birth_data_2.birth_date.year,
                    month=birth_data_2.birth_date.month,
                    day=birth_data_2.birth_date.day,
                    hour=birth_data_2.birth_time.hour,
                    minute=birth_data_2.birth_time.minute,
                    city=birth_data_2.location,
                    nation=birth_data_2.nation,
                    houses_system_identifier="W",
                )
                # Update birth_data with geocoded info
                birth_data_2.latitude = subject_2.lat
                birth_data_2.longitude = subject_2.lng
                birth_data_2.timezone = subject_2.tz_str
            except Exception as e:
                raise ValueError(f"Could not find location for second person: {birth_data_2.location}") from e

            active_points: List[AstrologicalPoint] = [
                "Sun",
                "Moon",
                "Mercury",
                "Venus",
                "Mars",
                "Jupiter",
                "Saturn",
                "Uranus",
                "Neptune",
                "Pluto",
            ]
            active_aspects: List[ActiveAspect] = [
                {"name": "conjunction", "orb": 5},
                {"name": "opposition", "orb": 5},
                {"name": "trine", "orb": 5},
                {"name": "square", "orb": 5},
                {"name": "sextile", "orb": 3},
            ]
            composite_subject = CompositeSubjectFactory(subject_1, subject_2).get_midpoint_composite_subject_model()
            chart_data = ChartDataFactory.create_composite_chart_data(
                composite_subject, active_points=active_points, active_aspects=active_aspects
            )

            drawer = CustomChartDrawer(chart_data=chart_data, theme="my-theme")

            svg_chart = drawer.generate_wheel_only_svg_string(minify=True, remove_css_variables=True)

            report = ReportGenerator(chart_data)
            report.print_report()

            logger.info("Composite chart generation successful")
            return svg_chart

        except Exception as e:
            if isinstance(e, ValueError):
                raise
            logger.error(f"Composite chart generation failed: {type(e).__name__}: {str(e)}")
            raise

    @staticmethod
    async def generate_transit(subject_1: AstrologicalSubjectModel, subject_2: AstrologicalSubjectModel) -> str:
        try:
            logger.info("Generating transit chart (no PII logged)")

            active_points: List[AstrologicalPoint] = [
                "Sun",
                "Moon",
                "Mercury",
                "Venus",
                "Mars",
                "Jupiter",
                "Saturn",
                "Uranus",
                "Neptune",
                "Pluto",
            ]
            active_aspects: List[ActiveAspect] = [
                {"name": "conjunction", "orb": 5},
                {"name": "opposition", "orb": 5},
                {"name": "trine", "orb": 5},
                {"name": "square", "orb": 5},
                {"name": "sextile", "orb": 3},
            ]

            chart_data = ChartDataFactory.create_transit_chart_data(
                natal_subject=subject_1,
                transit_subject=subject_2,
                active_points=active_points,
                active_aspects=active_aspects,
            )

            drawer = CustomChartDrawer(chart_data=chart_data, theme="my-theme")

            svg_chart = drawer.generate_wheel_only_svg_string(minify=True, remove_css_variables=True)

            logger.info("Composite chart generation successful")
            return svg_chart

        except Exception as e:
            logger.error(f"Composite chart generation failed: {type(e).__name__}: {str(e)}")
            raise

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

    @staticmethod
    async def generate_chart_by_type(chart_type: ChartSelection, birth_data_list: List[BirthData]) -> str:
        """Generate chart based on type (Natal or Composite).

        Unified interface for chart generation that routes to appropriate method.

        Args:
            chart_type: Type of chart to generate (Natal or Composite)
            birth_data_list: List of BirthData (1 for Natal, 2 for Composite)

        Returns:
            SVG chart as string

        Raises:
            ValueError: If invalid chart type or wrong number of birth data entries
        """
        if chart_type == ChartSelection.NATAL:
            if len(birth_data_list) != 1:
                raise ValueError(f"Natal chart requires exactly 1 birth data, got {len(birth_data_list)}")
            return await ChartService.generate_chart(birth_data_list[0])

        elif chart_type == ChartSelection.COMPOSITE:
            if len(birth_data_list) != 2:
                raise ValueError(f"Composite chart requires exactly 2 birth data entries, got {len(birth_data_list)}")

            # Create astrological subjects for both persons
            subject_1 = await ChartService._create_subject(birth_data_list[0])
            subject_2 = await ChartService._create_subject(birth_data_list[1])

            return await ChartService.generate_composite(subject_1, subject_2)

        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")

    @staticmethod
    async def _create_subject(birth_data: BirthData) -> AstrologicalSubjectModel:
        """Create AstrologicalSubjectModel from BirthData.

        Internal helper for composite chart generation.

        Args:
            birth_data: User's birth information

        Returns:
            AstrologicalSubjectModel for use in chart generation

        Raises:
            ValueError: If geocoding fails
        """
        try:
            subject = AstrologicalSubjectFactory.from_birth_data(
                name=birth_data.name,
                year=birth_data.birth_date.year,
                month=birth_data.birth_date.month,
                day=birth_data.birth_date.day,
                hour=birth_data.birth_time.hour,
                minute=birth_data.birth_time.minute,
                city=birth_data.location,
                nation=birth_data.nation,
            )

            # Update birth_data with geocoded information
            birth_data.latitude = subject.lat
            birth_data.longitude = subject.lng
            birth_data.timezone = subject.tz_str

            return subject

        except Exception as e:
            logger.error(f"Failed to create astrological subject: {type(e).__name__}")
            if "city" in str(e).lower() or "location" in str(e).lower():
                raise ValueError(
                    f"Could not find location '{birth_data.location}'. "
                    "Please try a more specific location (e.g., 'New York, USA' instead of 'NYC')"
                ) from e
            raise ValueError(f"Failed to create astrological subject: {str(e)}") from e
