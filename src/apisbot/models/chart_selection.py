"""Chart type selection models."""

from enum import Enum


class ChartSelection(str, Enum):
    """Available chart types for generation.

    Values:
        NATAL: Single person's birth chart (requires 1 birth data set)
        COMPOSITE: Relationship compatibility chart (requires 2 birth data sets)
    """

    NATAL = "natal"
    COMPOSITE = "composite"

    @property
    def display_name(self) -> str:
        """Get user-friendly display name for chart type."""
        return {
            ChartSelection.NATAL: "Natal Chart",
            ChartSelection.COMPOSITE: "Composite Chart",
        }[self]

    @property
    def description(self) -> str:
        """Get description of chart type for user."""
        return {
            ChartSelection.NATAL: "Personal birth chart showing planetary positions at your birth",
            ChartSelection.COMPOSITE: "Relationship chart comparing two people's birth data",
        }[self]

    @property
    def required_birth_data_count(self) -> int:
        """Get number of birth data sets required for this chart type."""
        return {
            ChartSelection.NATAL: 1,
            ChartSelection.COMPOSITE: 2,
        }[self]
