"""Tests for LocationData model."""

import pytest

from apisbot.models.location import LocationData


class TestLocationData:
    """Test LocationData model validation and functionality."""

    def test_location_data_creation(self):
        """Test basic LocationData instantiation."""
        loc_data = LocationData(
            city="New York",
            latitude=40.7128,
            longitude=-74.0060,
            timezone="America/New_York",
            display_name="New York, United States",
        )

        assert loc_data.city == "New York"
        assert loc_data.latitude == 40.7128
        assert loc_data.longitude == -74.0060
        assert loc_data.timezone == "America/New_York"
        assert loc_data.display_name == "New York, United States"
        assert loc_data.country is None

    def test_location_data_with_country(self):
        """Test LocationData with country field."""
        loc_data = LocationData(
            city="London",
            latitude=51.5074,
            longitude=-0.1278,
            timezone="Europe/London",
            display_name="London, United Kingdom",
            country="United Kingdom",
        )

        assert loc_data.country == "United Kingdom"

    def test_location_data_validates_latitude_too_high(self):
        """Test that latitude > 90 is rejected."""
        with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
            LocationData(
                city="Invalid",
                latitude=91.0,
                longitude=0.0,
                timezone="UTC",
                display_name="Invalid Location",
            )

    def test_location_data_validates_latitude_too_low(self):
        """Test that latitude < -90 is rejected."""
        with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
            LocationData(
                city="Invalid",
                latitude=-91.0,
                longitude=0.0,
                timezone="UTC",
                display_name="Invalid Location",
            )

    def test_location_data_validates_longitude_too_high(self):
        """Test that longitude > 180 is rejected."""
        with pytest.raises(ValueError, match="Longitude must be between -180 and 180"):
            LocationData(
                city="Invalid",
                latitude=0.0,
                longitude=181.0,
                timezone="UTC",
                display_name="Invalid Location",
            )

    def test_location_data_validates_longitude_too_low(self):
        """Test that longitude < -180 is rejected."""
        with pytest.raises(ValueError, match="Longitude must be between -180 and 180"):
            LocationData(
                city="Invalid",
                latitude=0.0,
                longitude=-181.0,
                timezone="UTC",
                display_name="Invalid Location",
            )

    def test_location_data_accepts_latitude_boundary_90(self):
        """Test that latitude = 90 (North Pole) is accepted."""
        loc_data = LocationData(
            city="North Pole",
            latitude=90.0,
            longitude=0.0,
            timezone="UTC",
            display_name="North Pole",
        )

        assert loc_data.latitude == 90.0

    def test_location_data_accepts_latitude_boundary_minus_90(self):
        """Test that latitude = -90 (South Pole) is accepted."""
        loc_data = LocationData(
            city="South Pole",
            latitude=-90.0,
            longitude=0.0,
            timezone="UTC",
            display_name="South Pole",
        )

        assert loc_data.latitude == -90.0

    def test_location_data_accepts_longitude_boundary_180(self):
        """Test that longitude = 180 is accepted."""
        loc_data = LocationData(
            city="Date Line",
            latitude=0.0,
            longitude=180.0,
            timezone="UTC",
            display_name="International Date Line",
        )

        assert loc_data.longitude == 180.0

    def test_location_data_accepts_longitude_boundary_minus_180(self):
        """Test that longitude = -180 is accepted."""
        loc_data = LocationData(
            city="Date Line",
            latitude=0.0,
            longitude=-180.0,
            timezone="UTC",
            display_name="International Date Line",
        )

        assert loc_data.longitude == -180.0

    def test_location_data_accepts_equator_prime_meridian(self):
        """Test that coordinates (0, 0) are accepted."""
        loc_data = LocationData(
            city="Null Island",
            latitude=0.0,
            longitude=0.0,
            timezone="UTC",
            display_name="Null Island",
        )

        assert loc_data.latitude == 0.0
        assert loc_data.longitude == 0.0

    def test_location_data_with_integer_coordinates(self):
        """Test that integer coordinates are accepted and stored as floats."""
        loc_data = LocationData(
            city="Test City",
            latitude=40,
            longitude=-74,
            timezone="America/New_York",
            display_name="Test City",
        )

        assert loc_data.latitude == 40.0
        assert loc_data.longitude == -74.0
