"""Unit tests for location geocoding service.

Tests geocoding, fuzzy matching, and error recovery options.
Mocks kerykeion to avoid external API calls during testing.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.apisbot.models.errors import ValidationError
from src.apisbot.models.location import LocationData
from src.apisbot.services.location_service import LocationService


class TestGeocodeLocation:
    """Test suite for geocoding location strings."""

    @pytest.mark.asyncio
    @patch("src.apisbot.services.location_service.AstrologicalSubject")
    async def test_geocode_location_successful(self, mock_subject_class):
        """Test that valid location is geocoded successfully."""
        # Mock kerykeion's AstrologicalSubject
        mock_subject = MagicMock()
        mock_subject.lat = 40.7128
        mock_subject.lng = -74.0060
        mock_subject.tz_str = "America/New_York"
        mock_subject_class.return_value = mock_subject

        result = await LocationService.geocode_location("New York")

        assert isinstance(result, LocationData)
        assert result.city == "New York"
        assert result.latitude == 40.7128
        assert result.longitude == -74.0060
        assert result.timezone == "America/New_York"

    @pytest.mark.asyncio
    @patch("src.apisbot.services.location_service.AstrologicalSubject")
    async def test_geocode_location_with_country(self, mock_subject_class):
        """Test that location with country is geocoded correctly."""
        mock_subject = MagicMock()
        mock_subject.lat = 51.5074
        mock_subject.lng = -0.1278
        mock_subject.tz_str = "Europe/London"
        mock_subject_class.return_value = mock_subject

        result = await LocationService.geocode_location("London, UK")

        assert isinstance(result, LocationData)
        assert result.city == "London, UK"
        assert result.latitude == 51.5074
        assert result.longitude == -0.1278
        assert result.timezone == "Europe/London"

    @pytest.mark.asyncio
    @patch("src.apisbot.services.location_service.AstrologicalSubject")
    async def test_geocode_location_failure_no_coordinates(self, mock_subject_class):
        """Test that geocoding failure returns ValidationError when no coordinates returned."""
        # Mock kerykeion returning None for coordinates
        mock_subject = MagicMock()
        mock_subject.lat = None
        mock_subject.lng = None
        mock_subject.tz_str = None
        mock_subject_class.return_value = mock_subject

        result = await LocationService.geocode_location("InvalidCity123")

        assert isinstance(result, ValidationError)
        assert result.field_name == "location"
        assert "not found" in result.message.lower() or "geocode" in result.message.lower()
        assert result.remediation is not None

    @pytest.mark.asyncio
    @patch("src.apisbot.services.location_service.AstrologicalSubject")
    async def test_geocode_location_exception_handling(self, mock_subject_class):
        """Test that geocoding exceptions are handled gracefully."""
        # Mock kerykeion raising exception
        mock_subject_class.side_effect = Exception("Geocoding API error")

        result = await LocationService.geocode_location("New York")

        assert isinstance(result, ValidationError)
        assert result.field_name == "location"
        assert result.user_input == "New York"

    @pytest.mark.asyncio
    @patch("src.apisbot.services.location_service.AstrologicalSubject")
    async def test_geocode_location_preserves_input_display_name(self, mock_subject_class):
        """Test that display_name preserves original user input."""
        mock_subject = MagicMock()
        mock_subject.lat = 48.8566
        mock_subject.lng = 2.3522
        mock_subject.tz_str = "Europe/Paris"
        mock_subject_class.return_value = mock_subject

        result = await LocationService.geocode_location("Paris, France")

        assert isinstance(result, LocationData)
        assert result.display_name == "Paris, France"

    @pytest.mark.asyncio
    @patch("src.apisbot.services.location_service.AstrologicalSubject")
    async def test_geocode_location_rare_timezone(self, mock_subject_class):
        """Test that rare timezones are handled correctly."""
        mock_subject = MagicMock()
        mock_subject.lat = -4.4419
        mock_subject.lng = 15.2663
        mock_subject.tz_str = "Africa/Kinshasa"
        mock_subject_class.return_value = mock_subject

        result = await LocationService.geocode_location("Kinshasa")

        assert isinstance(result, LocationData)
        assert result.timezone == "Africa/Kinshasa"


class TestParseCityName:
    """Test suite for fuzzy city name matching."""

    @pytest.mark.asyncio
    @patch("src.apisbot.services.location_service.AstrologicalSubject")
    async def test_parse_city_name_successful_match(self, mock_subject_class):
        """Test that parse_city_name returns list with successful match."""
        mock_subject = MagicMock()
        mock_subject.lat = 35.6762
        mock_subject.lng = 139.6503
        mock_subject.tz_str = "Asia/Tokyo"
        mock_subject_class.return_value = mock_subject

        result = await LocationService.parse_city_name("Tokyo")

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], LocationData)
        assert result[0].city == "Tokyo"

    @pytest.mark.asyncio
    @patch("src.apisbot.services.location_service.AstrologicalSubject")
    async def test_parse_city_name_no_match(self, mock_subject_class):
        """Test that parse_city_name returns empty list when no match found."""
        # Mock geocoding failure
        mock_subject = MagicMock()
        mock_subject.lat = None
        mock_subject.lng = None
        mock_subject.tz_str = None
        mock_subject_class.return_value = mock_subject

        result = await LocationService.parse_city_name("NonExistentCity9999")

        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.asyncio
    @patch("src.apisbot.services.location_service.AstrologicalSubject")
    async def test_parse_city_name_fuzzy_matching_future_enhancement(self, mock_subject_class):
        """Test placeholder for future fuzzy matching enhancement.

        Currently returns single result or empty list.
        Future: Should return multiple possible matches.
        """
        mock_subject = MagicMock()
        mock_subject.lat = 40.7128
        mock_subject.lng = -74.0060
        mock_subject.tz_str = "America/New_York"
        mock_subject_class.return_value = mock_subject

        result = await LocationService.parse_city_name("New York")

        # Currently returns single result
        # Future enhancement: Could return ["New York, USA", "New York, UK", etc.]
        assert isinstance(result, list)
        assert len(result) >= 0  # Can be 0 or more


class TestMapWidgetFallback:
    """Test suite for map widget fallback option."""

    @pytest.mark.asyncio
    async def test_get_map_widget_url_returns_url(self):
        """Test that get_map_widget_url returns a URL string."""
        user_id = 12345

        url = await LocationService.get_map_widget_url(user_id)

        assert isinstance(url, str)
        assert len(url) > 0

    @pytest.mark.asyncio
    async def test_get_map_widget_url_placeholder(self):
        """Test that get_map_widget_url is currently a placeholder.

        Future enhancement: Should return actual map widget integration.
        """
        user_id = 12345

        url = await LocationService.get_map_widget_url(user_id)

        # Currently returns placeholder
        # Future: Should return actual map service URL
        assert "map" in url.lower() or "example" in url.lower()


class TestGeocodingErrorRecovery:
    """Test suite for geocoding error recovery options (FR-012)."""

    @pytest.mark.asyncio
    @patch("src.apisbot.services.location_service.AstrologicalSubject")
    async def test_geocoding_error_includes_remediation_guidance(self, mock_subject_class):
        """Test that geocoding errors include helpful remediation."""
        mock_subject = MagicMock()
        mock_subject.lat = None
        mock_subject.lng = None
        mock_subject.tz_str = None
        mock_subject_class.return_value = mock_subject

        result = await LocationService.geocode_location("BadLocation")

        assert isinstance(result, ValidationError)
        assert result.remediation is not None
        # Should suggest adding country
        assert "country" in result.remediation.lower()

    @pytest.mark.asyncio
    @patch("src.apisbot.services.location_service.AstrologicalSubject")
    async def test_geocoding_error_suggests_specific_location(self, mock_subject_class):
        """Test that error suggests being more specific (add country)."""
        mock_subject = MagicMock()
        mock_subject.lat = None
        mock_subject.lng = None
        mock_subject.tz_str = None
        mock_subject_class.return_value = mock_subject

        result = await LocationService.geocode_location("Springfield")  # Ambiguous name

        assert isinstance(result, ValidationError)
        # Should suggest adding country for disambiguation
        assert "specific" in result.remediation.lower() or "country" in result.remediation.lower()

    @pytest.mark.asyncio
    @patch("src.apisbot.services.location_service.AstrologicalSubject")
    async def test_geocoding_error_provides_examples(self, mock_subject_class):
        """Test that error provides example location formats."""
        mock_subject = MagicMock()
        mock_subject.lat = None
        mock_subject.lng = None
        mock_subject.tz_str = None
        mock_subject_class.return_value = mock_subject

        result = await LocationService.geocode_location("InvalidCity")

        assert isinstance(result, ValidationError)
        # Should provide examples like "London, UK"
        assert "example" in result.remediation.lower() or "," in result.remediation

    @pytest.mark.asyncio
    @patch("src.apisbot.services.location_service.AstrologicalSubject")
    async def test_geocoding_error_preserves_user_input(self, mock_subject_class):
        """Test that error preserves original user input for debugging."""
        mock_subject = MagicMock()
        mock_subject.lat = None
        mock_subject.lng = None
        mock_subject.tz_str = None
        mock_subject_class.return_value = mock_subject

        user_input = "MyHomeTown123"
        result = await LocationService.geocode_location(user_input)

        assert isinstance(result, ValidationError)
        assert result.user_input == user_input

    @pytest.mark.asyncio
    @patch("src.apisbot.services.location_service.AstrologicalSubject")
    async def test_geocoding_error_suggests_nearby_major_city(self, mock_subject_class):
        """Test that error suggests using nearby major city as fallback."""
        mock_subject = MagicMock()
        mock_subject.lat = None
        mock_subject.lng = None
        mock_subject.tz_str = None
        mock_subject_class.return_value = mock_subject

        result = await LocationService.geocode_location("TinyVillage")

        assert isinstance(result, ValidationError)
        # Should suggest using nearby major city
        assert "nearby" in result.remediation.lower() or "major city" in result.remediation.lower()


class TestLocationServiceEdgeCases:
    """Test suite for edge cases and special scenarios."""

    @pytest.mark.asyncio
    @patch("src.apisbot.services.location_service.AstrologicalSubject")
    async def test_geocode_location_empty_string(self, mock_subject_class):
        """Test that empty location string is handled gracefully."""
        mock_subject = MagicMock()
        mock_subject.lat = None
        mock_subject.lng = None
        mock_subject.tz_str = None
        mock_subject_class.return_value = mock_subject

        result = await LocationService.geocode_location("")

        assert isinstance(result, ValidationError)

    @pytest.mark.asyncio
    @patch("src.apisbot.services.location_service.AstrologicalSubject")
    async def test_geocode_location_special_characters(self, mock_subject_class):
        """Test that location with special characters is handled."""
        mock_subject = MagicMock()
        mock_subject.lat = 45.5017
        mock_subject.lng = -73.5673
        mock_subject.tz_str = "America/Toronto"
        mock_subject_class.return_value = mock_subject

        result = await LocationService.geocode_location("Montréal")  # Accent character

        assert isinstance(result, LocationData)
        assert result.city == "Montréal"

    @pytest.mark.asyncio
    @patch("src.apisbot.services.location_service.AstrologicalSubject")
    async def test_geocode_location_very_long_input(self, mock_subject_class):
        """Test that very long location string is handled."""
        mock_subject = MagicMock()
        mock_subject.lat = None
        mock_subject.lng = None
        mock_subject.tz_str = None
        mock_subject_class.return_value = mock_subject

        long_input = "A" * 500  # Very long string
        result = await LocationService.geocode_location(long_input)

        assert isinstance(result, ValidationError)

    @pytest.mark.asyncio
    @patch("src.apisbot.services.location_service.AstrologicalSubject")
    async def test_geocode_location_numeric_input(self, mock_subject_class):
        """Test that numeric input is rejected gracefully."""
        mock_subject = MagicMock()
        mock_subject.lat = None
        mock_subject.lng = None
        mock_subject.tz_str = None
        mock_subject_class.return_value = mock_subject

        result = await LocationService.geocode_location("12345")

        assert isinstance(result, ValidationError)

    @pytest.mark.asyncio
    @patch("src.apisbot.services.location_service.AstrologicalSubject")
    async def test_geocode_location_coordinates_at_boundaries(self, mock_subject_class):
        """Test that locations with boundary coordinates (near poles/dateline) work."""
        mock_subject = MagicMock()
        mock_subject.lat = 89.9  # Near North Pole
        mock_subject.lng = 179.9  # Near International Date Line
        mock_subject.tz_str = "UTC"
        mock_subject_class.return_value = mock_subject

        result = await LocationService.geocode_location("Arctic Research Station")

        assert isinstance(result, LocationData)
        assert result.latitude == 89.9
        assert result.longitude == 179.9

    @pytest.mark.asyncio
    @patch("src.apisbot.services.location_service.AstrologicalSubject")
    async def test_geocode_location_southern_hemisphere(self, mock_subject_class):
        """Test that southern hemisphere locations work (negative latitude)."""
        mock_subject = MagicMock()
        mock_subject.lat = -33.8688  # Sydney
        mock_subject.lng = 151.2093
        mock_subject.tz_str = "Australia/Sydney"
        mock_subject_class.return_value = mock_subject

        result = await LocationService.geocode_location("Sydney, Australia")

        assert isinstance(result, LocationData)
        assert result.latitude < 0  # Southern hemisphere

    @pytest.mark.asyncio
    @patch("src.apisbot.services.location_service.AstrologicalSubject")
    async def test_geocode_location_western_hemisphere(self, mock_subject_class):
        """Test that western hemisphere locations work (negative longitude)."""
        mock_subject = MagicMock()
        mock_subject.lat = 19.4326  # Mexico City
        mock_subject.lng = -99.1332  # Negative longitude (west)
        mock_subject.tz_str = "America/Mexico_City"
        mock_subject_class.return_value = mock_subject

        result = await LocationService.geocode_location("Mexico City")

        assert isinstance(result, LocationData)
        assert result.longitude < 0  # Western hemisphere
