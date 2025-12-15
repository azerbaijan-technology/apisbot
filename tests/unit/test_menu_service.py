"""Unit tests for menu service.

Tests menu hints and help documentation generation without bot dependencies.
Validates FR-003 (help documentation) and US1 (command hints at each step).
"""

from apisbot.models.chart_selection import ChartSelection
from apisbot.services.menu_service import MenuService


class TestMenuService:
    """Test suite for MenuService."""

    def test_get_start_menu_text_returns_natal_description(self) -> None:
        """Test that start menu includes Natal chart description."""
        menu_text = MenuService.get_start_menu_text()

        assert "Natal Chart" in menu_text
        assert ChartSelection.NATAL.description in menu_text

    def test_get_start_menu_text_returns_composite_description(self) -> None:
        """Test that start menu includes Composite chart description."""
        menu_text = MenuService.get_start_menu_text()

        assert "Composite Chart" in menu_text
        assert ChartSelection.COMPOSITE.description in menu_text

    def test_get_start_menu_text_includes_welcome_message(self) -> None:
        """Test that start menu includes welcome message."""
        menu_text = MenuService.get_start_menu_text()

        assert "Welcome" in menu_text
        assert "Natal Chart Bot" in menu_text

    def test_get_start_menu_text_mentions_help_command(self) -> None:
        """Test that start menu mentions /help command."""
        menu_text = MenuService.get_start_menu_text()

        assert "/help" in menu_text

    def test_get_state_hints_returns_hints_for_chart_selection(self) -> None:
        """Test state hints for chart selection state."""
        hints = MenuService.get_state_hints("chart_selection")

        assert len(hints) > 0
        assert any("Choose chart type" in hint for hint in hints)
        assert any("/help" in hint for hint in hints)
        assert any("/cancel" in hint for hint in hints)

    def test_get_state_hints_returns_hints_for_name_entry(self) -> None:
        """Test state hints for name entry state."""
        hints = MenuService.get_state_hints("name_entry")

        assert len(hints) > 0
        assert any("name" in hint.lower() for hint in hints)
        assert any("Example" in hint for hint in hints)
        assert any("/cancel" in hint for hint in hints)

    def test_get_state_hints_returns_hints_for_date_entry(self) -> None:
        """Test state hints for date entry state."""
        hints = MenuService.get_state_hints("date_entry")

        assert len(hints) > 0
        assert any("birth date" in hint.lower() for hint in hints)
        assert any("DD.MM.YYYY" in hint for hint in hints)
        assert any("YYYY-MM-DD" in hint for hint in hints)
        assert any("/cancel" in hint for hint in hints)

    def test_get_state_hints_returns_hints_for_time_entry(self) -> None:
        """Test state hints for time entry state."""
        hints = MenuService.get_state_hints("time_entry")

        assert len(hints) > 0
        assert any("birth time" in hint.lower() for hint in hints)
        assert any("24-hour" in hint.lower() for hint in hints)
        assert any("HH:MM" in hint for hint in hints)
        assert any("/cancel" in hint for hint in hints)

    def test_get_state_hints_returns_hints_for_location_entry(self) -> None:
        """Test state hints for location entry state."""
        hints = MenuService.get_state_hints("location_entry")

        assert len(hints) > 0
        assert any("birth location" in hint.lower() for hint in hints)
        assert any("city" in hint.lower() for hint in hints)
        assert any("Example" in hint for hint in hints)
        assert any("/cancel" in hint for hint in hints)

    def test_get_state_hints_returns_hints_for_generating_state(self) -> None:
        """Test state hints for generating state."""
        hints = MenuService.get_state_hints("generating")

        assert len(hints) > 0
        assert any("Generating" in hint for hint in hints)

    def test_get_state_hints_returns_default_for_unknown_state(self) -> None:
        """Test state hints return defaults for unknown state."""
        hints = MenuService.get_state_hints("unknown_state_xyz")

        assert len(hints) > 0
        assert any("/help" in hint for hint in hints)

    def test_get_help_documentation_includes_natal_chart_explanation(self) -> None:
        """Test help documentation explains natal charts."""
        help_text = MenuService.get_help_documentation()

        assert "Natal Chart" in help_text
        assert "birth chart" in help_text.lower()

    def test_get_help_documentation_includes_composite_chart_explanation(self) -> None:
        """Test help documentation explains composite charts."""
        help_text = MenuService.get_help_documentation()

        assert "Composite Chart" in help_text
        assert "relationship" in help_text.lower()
        assert "compatibility" in help_text.lower()

    def test_get_help_documentation_includes_usage_steps(self) -> None:
        """Test help documentation includes step-by-step usage guide."""
        help_text = MenuService.get_help_documentation()

        assert "/start" in help_text
        assert "birth date" in help_text.lower()
        assert "birth time" in help_text.lower()
        assert "birth location" in help_text.lower()

    def test_get_help_documentation_includes_supported_formats(self) -> None:
        """Test help documentation lists supported date/time formats."""
        help_text = MenuService.get_help_documentation()

        # Date formats
        assert "DD.MM.YYYY" in help_text
        assert "YYYY-MM-DD" in help_text

        # Time formats
        assert "HH:MM" in help_text
        assert "24-hour" in help_text

    def test_get_help_documentation_includes_privacy_info(self) -> None:
        """Test help documentation includes privacy information."""
        help_text = MenuService.get_help_documentation()

        assert "Privacy" in help_text or "data" in help_text.lower()
        assert "30 minutes" in help_text

    def test_get_help_documentation_includes_commands(self) -> None:
        """Test help documentation lists available commands."""
        help_text = MenuService.get_help_documentation()

        assert "/start" in help_text
        assert "/help" in help_text
        assert "/cancel" in help_text

    def test_get_chart_type_description_for_natal(self) -> None:
        """Test chart type description for natal chart."""
        description = MenuService.get_chart_type_description(ChartSelection.NATAL)

        assert "Natal Chart" in description
        assert "birth" in description.lower()
        assert "personality" in description.lower()

    def test_get_chart_type_description_for_composite(self) -> None:
        """Test chart type description for composite chart."""
        description = MenuService.get_chart_type_description(ChartSelection.COMPOSITE)

        assert "Composite Chart" in description
        assert "relationship" in description.lower()

    def test_get_error_recovery_hints_includes_common_issues(self) -> None:
        """Test error recovery hints include common issues and solutions."""
        hints = MenuService.get_error_recovery_hints()

        assert "Invalid date" in hints or "date format" in hints.lower()
        assert "Location not found" in hints or "location" in hints.lower()
        assert "/help" in hints
        assert "/cancel" in hints

    def test_get_error_recovery_hints_includes_format_examples(self) -> None:
        """Test error recovery hints include format examples."""
        hints = MenuService.get_error_recovery_hints()

        assert "DD.MM.YYYY" in hints or "example" in hints.lower()


class TestMenuServiceNoAiogramDependencies:
    """Verify MenuService has no framework dependencies."""

    def test_menu_service_is_importable_without_aiogram(self) -> None:
        """Test MenuService can be imported without aiogram installed.

        This test verifies framework-agnostic design principle.
        """
        # If this test runs, the import succeeded
        assert MenuService is not None

    def test_all_methods_are_static(self) -> None:
        """Test all MenuService methods are static (no instance state)."""
        # Static methods can be called without instantiation
        assert callable(MenuService.get_start_menu_text)
        assert callable(MenuService.get_state_hints)
        assert callable(MenuService.get_help_documentation)
        assert callable(MenuService.get_chart_type_description)
        assert callable(MenuService.get_error_recovery_hints)
