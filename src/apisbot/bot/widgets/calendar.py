"""Calendar widget for date selection using aiogram-dialog.

Wraps aiogram-dialog calendar component for birth date selection.

Note: Widget created for future integration. Currently not used in handlers.
Full integration requires aiogram-dialog setup in main bot initialization.
"""

from datetime import date
from typing import Any, Dict

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Calendar
from aiogram_dialog.widgets.kbd.calendar_kbd import CalendarConfig

# Calendar configuration for birth date selection
BIRTH_DATE_CALENDAR_CONFIG = CalendarConfig(
    min_date=date(year=date.today().year - 200, month=1, day=1),  # 200 years ago
    max_date=date.today(),  # Today (no future dates)
)


class CalendarWidget:
    """Wrapper for aiogram-dialog calendar widget.

    Provides birth date selection with validation:
    - No future dates
    - No dates > 200 years ago
    - Invalid dates (Feb 30) prevented by calendar UI
    """

    @staticmethod
    def create_calendar(id: str = "birth_date_calendar") -> Calendar:
        """Create calendar widget for birth date selection.

        Args:
            id: Widget ID for callback handling

        Returns:
            Calendar widget configured for birth date constraints
        """
        return Calendar(
            id=id,
            config=BIRTH_DATE_CALENDAR_CONFIG,
            # on_click handler requires specific aiogram-dialog integration
            # This will be added during T034-T040 widget integration phase
        )

    # Note: on_date_selected handler signature depends on aiogram-dialog version
    # This is a placeholder for future integration (T034-T040)
    # Actual implementation will be added during widget integration phase

    @staticmethod
    def get_selected_date(manager: DialogManager) -> date | None:
        """Get selected date from dialog context.

        Args:
            manager: Dialog manager

        Returns:
            Selected date or None if not yet selected
        """
        return manager.dialog_data.get("selected_date")


# Getter function for dialog data display
async def get_calendar_data(dialog_manager: DialogManager, **kwargs: Any) -> Dict[str, Any]:
    """Provide calendar widget data to dialog.

    Args:
        dialog_manager: Dialog manager
        **kwargs: Additional context

    Returns:
        Dictionary with calendar data for rendering
    """
    selected_date = CalendarWidget.get_selected_date(dialog_manager)

    return {
        "selected_date": selected_date,
        "selected_date_display": dialog_manager.dialog_data.get("selected_date_display", "Not selected"),
    }
