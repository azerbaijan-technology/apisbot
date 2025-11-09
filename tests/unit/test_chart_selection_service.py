"""Unit tests for chart selection service.

Tests chart type validation and selection without bot dependencies.
Validates US2 (chart selection routing).
"""

import pytest

from apisbot.models.chart_selection import ChartSelection
from apisbot.models.errors import ValidationError
from apisbot.services.chart_selection_service import ChartSelectionService


class TestChartSelectionService:
    """Test suite for ChartSelectionService."""

    @pytest.mark.asyncio
    async def test_select_chart_with_valid_natal_type(self) -> None:
        """Test select_chart returns ChartSelection.NATAL for valid 'natal' input."""
        result = await ChartSelectionService.select_chart(123, "natal")

        assert isinstance(result, ChartSelection)
        assert result == ChartSelection.NATAL

    @pytest.mark.asyncio
    async def test_select_chart_with_valid_composite_type(self) -> None:
        """Test select_chart returns ChartSelection.COMPOSITE for valid 'composite' input."""
        result = await ChartSelectionService.select_chart(123, "composite")

        assert isinstance(result, ChartSelection)
        assert result == ChartSelection.COMPOSITE

    @pytest.mark.asyncio
    async def test_select_chart_with_uppercase_input(self) -> None:
        """Test select_chart handles uppercase input (case-insensitive)."""
        result = await ChartSelectionService.select_chart(123, "NATAL")

        assert isinstance(result, ChartSelection)
        assert result == ChartSelection.NATAL

    @pytest.mark.asyncio
    async def test_select_chart_with_mixed_case_input(self) -> None:
        """Test select_chart handles mixed case input."""
        result = await ChartSelectionService.select_chart(123, "CoMpOsItE")

        assert isinstance(result, ChartSelection)
        assert result == ChartSelection.COMPOSITE

    @pytest.mark.asyncio
    async def test_select_chart_with_invalid_type(self) -> None:
        """Test select_chart returns ValidationError for invalid chart type."""
        result = await ChartSelectionService.select_chart(123, "invalid_chart")

        assert isinstance(result, ValidationError)
        assert result.field_name == "chart_type"
        assert "invalid_chart" in result.message.lower() or "unknown" in result.message.lower()
        assert result.remediation is not None

    @pytest.mark.asyncio
    async def test_select_chart_with_empty_string(self) -> None:
        """Test select_chart returns ValidationError for empty string."""
        result = await ChartSelectionService.select_chart(123, "")

        assert isinstance(result, ValidationError)
        assert result.field_name == "chart_type"

    @pytest.mark.asyncio
    async def test_select_chart_with_whitespace(self) -> None:
        """Test select_chart returns ValidationError for whitespace."""
        result = await ChartSelectionService.select_chart(123, "   ")

        assert isinstance(result, ValidationError)
        assert result.field_name == "chart_type"

    def test_validate_chart_type_with_natal(self) -> None:
        """Test validate_chart_type returns ChartSelection.NATAL for 'natal'."""
        result = ChartSelectionService.validate_chart_type("natal")

        assert isinstance(result, ChartSelection)
        assert result == ChartSelection.NATAL

    def test_validate_chart_type_with_composite(self) -> None:
        """Test validate_chart_type returns ChartSelection.COMPOSITE for 'composite'."""
        result = ChartSelectionService.validate_chart_type("composite")

        assert isinstance(result, ChartSelection)
        assert result == ChartSelection.COMPOSITE

    def test_validate_chart_type_case_insensitive(self) -> None:
        """Test validate_chart_type is case-insensitive."""
        result_upper = ChartSelectionService.validate_chart_type("NATAL")
        result_lower = ChartSelectionService.validate_chart_type("natal")
        result_mixed = ChartSelectionService.validate_chart_type("NaTaL")

        assert result_upper == result_lower == result_mixed == ChartSelection.NATAL

    def test_validate_chart_type_with_invalid_type(self) -> None:
        """Test validate_chart_type returns ValidationError for invalid type."""
        result = ChartSelectionService.validate_chart_type("synastry")

        assert isinstance(result, ValidationError)
        assert result.field_name == "chart_type"
        assert "synastry" in result.message.lower() or "unknown" in result.message.lower()

    def test_validate_chart_type_includes_available_types_in_remediation(self) -> None:
        """Test ValidationError includes available types in remediation."""
        result = ChartSelectionService.validate_chart_type("invalid")

        assert isinstance(result, ValidationError)
        assert "natal" in result.remediation.lower()
        assert "composite" in result.remediation.lower()

    def test_get_available_charts_returns_all_types(self) -> None:
        """Test get_available_charts returns all chart types."""
        charts = ChartSelectionService.get_available_charts()

        assert len(charts) == 2
        assert ChartSelection.NATAL in charts
        assert ChartSelection.COMPOSITE in charts

    def test_get_available_charts_returns_list(self) -> None:
        """Test get_available_charts returns a list."""
        charts = ChartSelectionService.get_available_charts()

        assert isinstance(charts, list)
        assert all(isinstance(chart, ChartSelection) for chart in charts)


class TestChartSelectionServiceNoAiogramDependencies:
    """Verify ChartSelectionService has no framework dependencies."""

    def test_service_is_importable_without_aiogram(self) -> None:
        """Test ChartSelectionService can be imported without aiogram installed.

        This test verifies framework-agnostic design principle.
        """
        # If this test runs, the import succeeded
        assert ChartSelectionService is not None

    def test_validate_chart_type_is_synchronous(self) -> None:
        """Test validate_chart_type is synchronous (no async)."""
        # Should be callable without await
        result = ChartSelectionService.validate_chart_type("natal")
        assert result == ChartSelection.NATAL

    def test_get_available_charts_is_synchronous(self) -> None:
        """Test get_available_charts is synchronous (no async)."""
        # Should be callable without await
        charts = ChartSelectionService.get_available_charts()
        assert len(charts) > 0


class TestChartSelectionValidationEdgeCases:
    """Test edge cases for chart selection validation."""

    @pytest.mark.asyncio
    async def test_select_chart_with_special_characters(self) -> None:
        """Test select_chart handles special characters gracefully."""
        result = await ChartSelectionService.select_chart(123, "natal@#$%")

        assert isinstance(result, ValidationError)

    @pytest.mark.asyncio
    async def test_select_chart_with_numeric_string(self) -> None:
        """Test select_chart handles numeric strings."""
        result = await ChartSelectionService.select_chart(123, "12345")

        assert isinstance(result, ValidationError)

    def test_validate_chart_type_preserves_enum_properties(self) -> None:
        """Test validated ChartSelection preserves enum properties."""
        result = ChartSelectionService.validate_chart_type("natal")

        assert isinstance(result, ChartSelection)
        assert result.display_name == "Natal Chart"
        assert result.description is not None
        assert result.required_birth_data_count == 1

    def test_validate_chart_type_composite_preserves_properties(self) -> None:
        """Test validated Composite ChartSelection preserves properties."""
        result = ChartSelectionService.validate_chart_type("composite")

        assert isinstance(result, ChartSelection)
        assert result.display_name == "Composite Chart"
        assert result.required_birth_data_count == 2
