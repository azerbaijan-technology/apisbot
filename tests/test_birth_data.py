"""Tests for BirthData model."""

from datetime import date, time, timedelta

from apisbot.models.birth_data import BirthData


class TestBirthData:
    """Test BirthData model validation."""

    def test_birth_data_creation(self):
        """Test basic BirthData instantiation."""
        birth_data = BirthData(
            name="John Doe",
            birth_date=date(1990, 5, 15),
            birth_time=time(14, 30),
            location="New York",
        )

        assert birth_data.name == "John Doe"
        assert birth_data.birth_date == date(1990, 5, 15)
        assert birth_data.birth_time == time(14, 30)
        assert birth_data.location == "New York"
        assert birth_data.latitude is None
        assert birth_data.longitude is None
        assert birth_data.timezone is None

    def test_birth_data_with_coordinates(self):
        """Test BirthData with geocoded coordinates."""
        birth_data = BirthData(
            name="Jane Smith",
            birth_date=date(1985, 12, 25),
            birth_time=time(8, 0),
            location="London",
            latitude=51.5074,
            longitude=-0.1278,
            timezone="Europe/London",
        )

        assert birth_data.latitude == 51.5074
        assert birth_data.longitude == -0.1278
        assert birth_data.timezone == "Europe/London"

    def test_validate_name_valid(self):
        """Test name validation with valid names."""
        valid_names = [
            "John",
            "Mary Jane",
            "José García",
            "李明",
            "A",
            "a" * 100,  # Max length
            "123 John",  # With numbers
            "O'Brien",  # With apostrophe
        ]

        for name in valid_names:
            birth_data = BirthData(
                name=name,
                birth_date=date(1990, 1, 1),
                birth_time=time(12, 0),
                location="Test",
            )
            assert birth_data.validate_name(), f"Name '{name}' should be valid"

    def test_validate_name_invalid(self):
        """Test name validation with invalid names."""
        invalid_names = [
            "",  # Empty
            "   ",  # Only whitespace
            "a" * 101,  # Too long
            "123",  # Only numbers
            "!@#$%",  # Only special characters
        ]

        for name in invalid_names:
            birth_data = BirthData(
                name=name,
                birth_date=date(1990, 1, 1),
                birth_time=time(12, 0),
                location="Test",
            )
            assert not birth_data.validate_name(), f"Name '{name}' should be invalid"

    def test_validate_date_valid(self):
        """Test date validation with valid dates."""
        today = date.today()
        valid_dates = [
            today,  # Today
            today - timedelta(days=1),  # Yesterday
            date(1990, 5, 15),  # Random past date
            date(1900, 1, 1),  # Old date
            today - timedelta(days=150 * 365 - 1),  # Just within 150 years
        ]

        for birth_date in valid_dates:
            birth_data = BirthData(
                name="Test",
                birth_date=birth_date,
                birth_time=time(12, 0),
                location="Test",
            )
            assert birth_data.validate_date(), f"Date {birth_date} should be valid"

    def test_validate_date_invalid(self):
        """Test date validation with invalid dates."""
        today = date.today()
        invalid_dates = [
            today + timedelta(days=1),  # Future date
            today - timedelta(days=150 * 365 + 1),  # More than 150 years ago
        ]

        for birth_date in invalid_dates:
            birth_data = BirthData(
                name="Test",
                birth_date=birth_date,
                birth_time=time(12, 0),
                location="Test",
            )
            assert not birth_data.validate_date(), f"Date {birth_date} should be invalid"

    def test_validate_date_boundary(self):
        """Test date validation at exact boundaries."""
        today = date.today()

        # Exactly 150 years ago should be valid
        exactly_150_years = today - timedelta(days=150 * 365)
        birth_data = BirthData(
            name="Test",
            birth_date=exactly_150_years,
            birth_time=time(12, 0),
            location="Test",
        )
        assert birth_data.validate_date()

        # Today should be valid
        birth_data.birth_date = today
        assert birth_data.validate_date()
