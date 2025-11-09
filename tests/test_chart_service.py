"""Tests for chart_service."""

from datetime import date, time
from unittest.mock import MagicMock, patch

import pytest

from apisbot.models.birth_data import BirthData
from apisbot.services.chart_service import ChartService


class TestChartService:
    """Test ChartService for natal chart generation."""

    @pytest.mark.asyncio
    @patch("apisbot.services.chart_service.AstrologicalSubjectFactory")
    @patch("apisbot.services.chart_service.ChartDataFactory")
    @patch("apisbot.services.chart_service.ChartDrawer")
    async def test_generate_chart_success(self, mock_drawer_class, mock_chart_data_factory, mock_subject_factory):
        """Test successful chart generation."""
        # Setup mocks
        mock_subject = MagicMock()
        mock_subject.lat = 40.7128
        mock_subject.lng = -74.0060
        mock_subject.tz_str = "America/New_York"
        mock_subject_factory.from_birth_data.return_value = mock_subject

        mock_chart_data = MagicMock()
        mock_chart_data_factory.create_natal_chart_data.return_value = mock_chart_data

        mock_drawer = MagicMock()
        mock_drawer.generate_wheel_only_svg_string.return_value = "<svg>test chart</svg>"
        mock_drawer_class.return_value = mock_drawer

        # Create test data
        birth_data = BirthData(
            name="John Doe",
            birth_date=date(1990, 5, 15),
            birth_time=time(14, 30),
            location="New York",
        )

        # Execute
        result = await ChartService.generate_chart(birth_data)

        # Verify
        assert result == "<svg>test chart</svg>"
        assert birth_data.latitude == 40.7128
        assert birth_data.longitude == -74.0060
        assert birth_data.timezone == "America/New_York"

        mock_subject_factory.from_birth_data.assert_called_once_with(
            name="John Doe",
            year=1990,
            month=5,
            day=15,
            hour=14,
            minute=30,
            city="New York",
            nation=" ",
        )
        mock_chart_data_factory.create_natal_chart_data.assert_called_once_with(mock_subject)
        mock_drawer_class.assert_called_once_with(mock_chart_data)
        mock_drawer.generate_wheel_only_svg_string.assert_called_once_with(minify=True, remove_css_variables=True)

    @pytest.mark.asyncio
    @patch("apisbot.services.chart_service.AstrologicalSubjectFactory")
    async def test_generate_chart_location_error(self, mock_subject_factory):
        """Test chart generation with location geocoding error."""
        # Setup mock to raise location error
        mock_subject_factory.from_birth_data.side_effect = Exception("city not found")

        birth_data = BirthData(
            name="John Doe",
            birth_date=date(1990, 5, 15),
            birth_time=time(14, 30),
            location="InvalidLocation123",
        )

        with pytest.raises(ValueError, match="Could not find location"):
            await ChartService.generate_chart(birth_data)

    @pytest.mark.asyncio
    @patch("apisbot.services.chart_service.AstrologicalSubjectFactory")
    async def test_generate_chart_generic_error(self, mock_subject_factory):
        """Test chart generation with generic error."""
        mock_subject_factory.from_birth_data.side_effect = Exception("Some other error")

        birth_data = BirthData(
            name="John Doe",
            birth_date=date(1990, 5, 15),
            birth_time=time(14, 30),
            location="New York",
        )

        with pytest.raises(ValueError, match="Failed to generate natal chart"):
            await ChartService.generate_chart(birth_data)

    @pytest.mark.asyncio
    @patch("apisbot.services.chart_service.ChartService._create_subject")
    @patch("apisbot.services.chart_service.CompositeSubjectFactory")
    @patch("apisbot.services.chart_service.ChartDataFactory")
    @patch("apisbot.services.chart_service.ChartDrawer")
    async def test_generate_composite_success(
        self, mock_drawer_class, mock_chart_data_factory, mock_composite_factory_class, mock_create_subject
    ):
        """Test successful composite chart generation."""
        # Setup mocks for subjects
        mock_subject_1 = MagicMock()
        mock_subject_1.lat = 40.7128
        mock_subject_1.lng = -74.0060
        mock_subject_1.tz_str = "America/New_York"

        mock_subject_2 = MagicMock()
        mock_subject_2.lat = 51.5074
        mock_subject_2.lng = -0.1278
        mock_subject_2.tz_str = "Europe/London"

        mock_create_subject.side_effect = [mock_subject_1, mock_subject_2]

        # Setup composite mock
        mock_composite_subject = MagicMock()
        mock_composite_factory = MagicMock()
        mock_composite_factory.get_midpoint_composite_subject_model.return_value = mock_composite_subject
        mock_composite_factory_class.return_value = mock_composite_factory

        mock_chart_data = MagicMock()
        mock_chart_data_factory.create_composite_chart_data.return_value = mock_chart_data

        mock_drawer = MagicMock()
        mock_drawer.generate_wheel_only_svg_string.return_value = "<svg>composite chart</svg>"
        mock_drawer_class.return_value = mock_drawer

        # Create test data
        birth_data_1 = BirthData(
            name="Person 1",
            birth_date=date(1990, 5, 15),
            birth_time=time(14, 30),
            location="New York",
        )
        birth_data_2 = BirthData(
            name="Person 2",
            birth_date=date(1985, 12, 25),
            birth_time=time(8, 0),
            location="London",
        )

        # Execute using generate_chart_by_type
        from apisbot.models.chart_selection import ChartSelection

        result = await ChartService.generate_chart_by_type(ChartSelection.COMPOSITE, [birth_data_1, birth_data_2])

        # Verify
        assert result == "<svg>composite chart</svg>"
        assert mock_create_subject.call_count == 2

    @pytest.mark.asyncio
    @patch("apisbot.services.chart_service.ChartService._create_subject")
    async def test_generate_composite_first_person_location_error(self, mock_create_subject):
        """Test composite chart with first person's location error."""
        mock_create_subject.side_effect = ValueError("Could not find location 'InvalidCity1'")

        birth_data_1 = BirthData(
            name="Person 1",
            birth_date=date(1990, 5, 15),
            birth_time=time(14, 30),
            location="InvalidCity1",
        )
        birth_data_2 = BirthData(
            name="Person 2",
            birth_date=date(1985, 12, 25),
            birth_time=time(8, 0),
            location="London",
        )

        from apisbot.models.chart_selection import ChartSelection

        with pytest.raises(ValueError, match="Could not find location"):
            await ChartService.generate_chart_by_type(ChartSelection.COMPOSITE, [birth_data_1, birth_data_2])

    @pytest.mark.asyncio
    @patch("apisbot.services.chart_service.ChartService._create_subject")
    async def test_generate_composite_second_person_location_error(self, mock_create_subject):
        """Test composite chart with second person's location error."""
        mock_subject_1 = MagicMock()
        mock_subject_1.lat = 40.7128
        mock_subject_1.lng = -74.0060
        mock_subject_1.tz_str = "America/New_York"

        mock_create_subject.side_effect = [mock_subject_1, ValueError("Could not find location 'InvalidCity2'")]

        birth_data_1 = BirthData(
            name="Person 1",
            birth_date=date(1990, 5, 15),
            birth_time=time(14, 30),
            location="New York",
        )
        birth_data_2 = BirthData(
            name="Person 2",
            birth_date=date(1985, 12, 25),
            birth_time=time(8, 0),
            location="InvalidCity2",
        )

        from apisbot.models.chart_selection import ChartSelection

        with pytest.raises(ValueError, match="Could not find location"):
            await ChartService.generate_chart_by_type(ChartSelection.COMPOSITE, [birth_data_1, birth_data_2])

    @pytest.mark.asyncio
    @patch("apisbot.services.chart_service.AstrologicalSubject")
    async def test_validate_location_success(self, mock_subject_class):
        """Test successful location validation."""
        mock_subject = MagicMock()
        mock_subject.lat = 40.7128
        mock_subject.lng = -74.0060
        mock_subject.tz_str = "America/New_York"
        mock_subject_class.return_value = mock_subject

        result = await ChartService.validate_location("New York")

        assert result == (40.7128, -74.0060, "America/New_York")

    @pytest.mark.asyncio
    @patch("apisbot.services.chart_service.AstrologicalSubject")
    async def test_validate_location_no_coordinates(self, mock_subject_class):
        """Test location validation when no coordinates are returned."""
        mock_subject = MagicMock()
        mock_subject.lat = None
        mock_subject.lng = None
        mock_subject_class.return_value = mock_subject

        result = await ChartService.validate_location("InvalidLocation")

        assert result is None

    @pytest.mark.asyncio
    @patch("apisbot.services.chart_service.AstrologicalSubject")
    async def test_validate_location_exception(self, mock_subject_class):
        """Test location validation with exception."""
        mock_subject_class.side_effect = Exception("Geocoding failed")

        result = await ChartService.validate_location("New York")

        assert result is None
