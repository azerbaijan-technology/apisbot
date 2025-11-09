"""Chart selection service for routing to appropriate chart flow.

Framework-agnostic service with no aiogram dependencies.
"""

from typing import List

from ..models.chart_selection import ChartSelection
from ..models.errors import ValidationError


class ChartSelectionService:
    """Service for handling chart type selection.

    Implements US2: Chart selection menu routing.
    No aiogram dependencies: Fully testable without bot infrastructure.
    """

    @staticmethod
    async def select_chart(user_id: int, chart_type: str) -> ChartSelection | ValidationError:
        """Validate and select chart type for user.

        Args:
            user_id: Telegram user ID
            chart_type: Chart type string (e.g., 'natal', 'composite')

        Returns:
            ChartSelection if valid, ValidationError if invalid type
        """
        try:
            # Validate chart type
            validated_type = ChartSelectionService.validate_chart_type(chart_type)

            if isinstance(validated_type, ValidationError):
                return validated_type

            return validated_type

        except Exception:
            return ValidationError(
                field_name="chart_type",
                message=f"Invalid chart type: {chart_type}",
                remediation="Please select a valid chart type from the menu.",
                user_input=chart_type,
            )

    @staticmethod
    def validate_chart_type(chart_type: str) -> ChartSelection | ValidationError:
        """Validate chart type string.

        Args:
            chart_type: Chart type string (e.g., 'natal', 'composite')

        Returns:
            ChartSelection if valid, ValidationError if invalid
        """
        try:
            # Try to parse as ChartSelection enum
            return ChartSelection(chart_type.lower())
        except ValueError:
            available_types = [ct.value for ct in ChartSelection]
            return ValidationError(
                field_name="chart_type",
                message=f"Unknown chart type: {chart_type}",
                remediation=f"Available chart types: {', '.join(available_types)}",
                user_input=chart_type,
            )

    @staticmethod
    def get_available_charts() -> List[ChartSelection]:
        """Get list of available chart types.

        Returns:
            List of all available ChartSelection types
        """
        return list(ChartSelection)
