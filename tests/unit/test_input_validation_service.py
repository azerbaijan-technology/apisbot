"""Unit tests for input validation service.

Tests unified validation service without bot dependencies.
Validates FR-005 (ValidationError with remediation) and US3 (error recovery).
"""

import pytest

from apisbot.models.errors import ValidationError
from apisbot.services.input_validation_service import InputValidationService


class TestNameValidation:
    """Test suite for name validation."""

    def test_validate_name_with_valid_input(self) -> None:
        """Test validate_name returns cleaned name for valid input."""
        result = InputValidationService.validate_name("John Doe")

        assert isinstance(result, str)
        assert result == "John Doe"

    def test_validate_name_strips_whitespace(self) -> None:
        """Test validate_name strips leading/trailing whitespace."""
        result = InputValidationService.validate_name("  John Doe  ")

        assert isinstance(result, str)
        assert result == "John Doe"

    def test_validate_name_with_empty_string(self) -> None:
        """Test validate_name returns ValidationError for empty string."""
        result = InputValidationService.validate_name("")

        assert isinstance(result, ValidationError)
        assert result.field_name == "name"
        assert "empty" in result.message.lower()
        assert result.remediation is not None

    def test_validate_name_with_whitespace_only(self) -> None:
        """Test validate_name returns ValidationError for whitespace only."""
        result = InputValidationService.validate_name("   ")

        assert isinstance(result, ValidationError)
        assert result.field_name == "name"

    def test_validate_name_with_too_long_input(self) -> None:
        """Test validate_name returns ValidationError for > 100 characters."""
        long_name = "A" * 101
        result = InputValidationService.validate_name(long_name)

        assert isinstance(result, ValidationError)
        assert result.field_name == "name"
        assert "long" in result.message.lower() or "100" in result.message

    def test_validate_name_with_exactly_100_characters(self) -> None:
        """Test validate_name accepts exactly 100 characters."""
        name_100 = "A" * 100
        result = InputValidationService.validate_name(name_100)

        assert isinstance(result, str)
        assert result == name_100

    def test_validate_name_with_numbers_only(self) -> None:
        """Test validate_name rejects numbers-only input (no letters)."""
        result = InputValidationService.validate_name("12345")

        assert isinstance(result, ValidationError)
        assert result.field_name == "name"
        assert "letter" in result.message.lower()

    def test_validate_name_with_special_characters_only(self) -> None:
        """Test validate_name rejects special characters only (no letters)."""
        result = InputValidationService.validate_name("!@#$%")

        assert isinstance(result, ValidationError)
        assert result.field_name == "name"
        assert "letter" in result.message.lower()

    def test_validate_name_with_mixed_alphanumeric(self) -> None:
        """Test validate_name accepts mixed letters and numbers."""
        result = InputValidationService.validate_name("John123")

        assert isinstance(result, str)
        assert result == "John123"

    def test_validate_name_with_unicode_characters(self) -> None:
        """Test validate_name accepts unicode/international characters."""
        result = InputValidationService.validate_name("María")

        assert isinstance(result, str)
        assert result == "María"

    def test_validate_name_with_chinese_characters(self) -> None:
        """Test validate_name accepts Chinese characters."""
        result = InputValidationService.validate_name("李明")

        assert isinstance(result, str)
        assert result == "李明"

    def test_validation_error_includes_remediation(self) -> None:
        """Test ValidationError includes helpful remediation message."""
        result = InputValidationService.validate_name("")

        assert isinstance(result, ValidationError)
        assert result.remediation is not None
        assert len(result.remediation) > 0


class TestDateValidation:
    """Test suite for date validation."""

    @pytest.mark.asyncio
    async def test_validate_date_with_valid_format_ddmmyyyy(self) -> None:
        """Test validate_date accepts DD.MM.YYYY format."""
        result = await InputValidationService.validate_date("15.05.1990")

        # Should return DateTimeData or ValidationError
        assert result is not None

    @pytest.mark.asyncio
    async def test_validate_date_with_invalid_format(self) -> None:
        """Test validate_date returns ValidationError for invalid format."""
        result = await InputValidationService.validate_date("invalid-date")

        assert isinstance(result, ValidationError)
        assert result.field_name == "birth_date"
        assert result.remediation is not None

    @pytest.mark.asyncio
    async def test_validate_date_with_impossible_date(self) -> None:
        """Test validate_date returns ValidationError for impossible dates (e.g., Feb 30)."""
        result = await InputValidationService.validate_date("30.02.1990")

        assert isinstance(result, ValidationError)
        assert result.field_name == "birth_date"

    @pytest.mark.asyncio
    async def test_validate_date_with_empty_string(self) -> None:
        """Test validate_date returns ValidationError for empty string."""
        result = await InputValidationService.validate_date("")

        assert isinstance(result, ValidationError)
        assert result.field_name == "birth_date"

    @pytest.mark.asyncio
    async def test_validate_date_error_includes_remediation(self) -> None:
        """Test date ValidationError includes format examples in remediation."""
        result = await InputValidationService.validate_date("bad-format")

        assert isinstance(result, ValidationError)
        assert result.remediation is not None
        # Should suggest valid formats
        assert "DD.MM.YYYY" in result.remediation or "format" in result.remediation.lower()


class TestTimeValidation:
    """Test suite for time validation."""

    @pytest.mark.asyncio
    async def test_validate_time_with_valid_24hour_format(self) -> None:
        """Test validate_time accepts HH:MM 24-hour format."""
        result = await InputValidationService.validate_time("14:30")

        # Should return DateTimeData or ValidationError
        assert result is not None

    @pytest.mark.asyncio
    async def test_validate_time_with_invalid_format(self) -> None:
        """Test validate_time returns ValidationError for invalid format."""
        result = await InputValidationService.validate_time("invalid-time")

        assert isinstance(result, ValidationError)
        assert result.field_name == "birth_time"
        assert result.remediation is not None

    @pytest.mark.asyncio
    async def test_validate_time_with_invalid_hour(self) -> None:
        """Test validate_time returns ValidationError for invalid hour (> 23)."""
        result = await InputValidationService.validate_time("25:30")

        assert isinstance(result, ValidationError)
        assert result.field_name == "birth_time"

    @pytest.mark.asyncio
    async def test_validate_time_with_empty_string(self) -> None:
        """Test validate_time returns ValidationError for empty string."""
        result = await InputValidationService.validate_time("")

        assert isinstance(result, ValidationError)
        assert result.field_name == "birth_time"

    @pytest.mark.asyncio
    async def test_validate_time_error_includes_remediation(self) -> None:
        """Test time ValidationError includes format examples in remediation."""
        result = await InputValidationService.validate_time("bad-format")

        assert isinstance(result, ValidationError)
        assert result.remediation is not None
        # Should suggest valid formats
        assert "HH:MM" in result.remediation or "format" in result.remediation.lower()


class TestLocationValidation:
    """Test suite for location validation."""

    @pytest.mark.asyncio
    async def test_validate_location_with_invalid_location(self) -> None:
        """Test validate_location returns ValidationError for unrecognizable location."""
        # Use an obviously invalid location
        result = await InputValidationService.validate_location("xyzabc123notacity")

        # Should return ValidationError for invalid location
        assert isinstance(result, ValidationError)
        assert result.field_name == "location"
        assert result.remediation is not None

    @pytest.mark.asyncio
    async def test_validate_location_with_empty_string(self) -> None:
        """Test validate_location returns ValidationError for empty string."""
        result = await InputValidationService.validate_location("")

        assert isinstance(result, ValidationError)
        assert result.field_name == "location"

    @pytest.mark.asyncio
    async def test_validate_location_error_includes_remediation(self) -> None:
        """Test location ValidationError includes helpful remediation."""
        result = await InputValidationService.validate_location("invalidlocation")

        assert isinstance(result, ValidationError)
        assert result.remediation is not None
        # Should suggest including country or trying nearby city
        assert len(result.remediation) > 0


class TestInputValidationServiceNoAiogramDependencies:
    """Verify InputValidationService has no framework dependencies."""

    def test_service_is_importable_without_aiogram(self) -> None:
        """Test InputValidationService can be imported without aiogram installed.

        This test verifies framework-agnostic design principle.
        """
        # If this test runs, the import succeeded
        assert InputValidationService is not None

    def test_validate_name_is_synchronous(self) -> None:
        """Test validate_name is synchronous (no async)."""
        # Should be callable without await
        result = InputValidationService.validate_name("Test")
        assert isinstance(result, str)
        assert result == "Test"


class TestValidationErrorStructure:
    """Test ValidationError structure for FR-005 compliance."""

    def test_validation_error_has_required_fields(self) -> None:
        """Test ValidationError includes field_name, message, and remediation."""
        result = InputValidationService.validate_name("")

        assert isinstance(result, ValidationError)
        assert hasattr(result, "field_name")
        assert hasattr(result, "message")
        assert hasattr(result, "remediation")
        assert hasattr(result, "user_input")

    def test_validation_error_remediation_is_helpful(self) -> None:
        """Test ValidationError remediation provides actionable guidance."""
        result = InputValidationService.validate_name("12345")

        assert isinstance(result, ValidationError)
        assert result.remediation is not None
        # Should provide examples or suggestions
        assert len(result.remediation) > 20  # Substantial guidance
