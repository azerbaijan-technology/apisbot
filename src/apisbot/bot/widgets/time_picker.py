"""Time picker widget for birth time selection.

Custom inline button grid for 24-hour time selection.
Uses aiogram inline keyboards (no aiogram-dialog dependency for this widget).

Note: Widget created for future integration. Currently not used in handlers.
Full integration will be added during T034-T040 widget integration phase.
"""

from datetime import time
from typing import List, Optional

from aiogram.types import CallbackQuery, InaccessibleMessage, InlineKeyboardButton, InlineKeyboardMarkup


class TimePickerWidget:
    """Time picker with inline button grid for hour/minute selection.

    24-hour format (unambiguous, no AM/PM confusion).
    Two-step selection: Hour → Minute
    """

    @staticmethod
    def create_hour_keyboard() -> InlineKeyboardMarkup:
        """Create inline keyboard for hour selection (0-23).

        Layout: 6 rows x 4 columns for 24 hours

        Returns:
            InlineKeyboardMarkup with hour selection buttons
        """
        buttons: List[List[InlineKeyboardButton]] = []

        # Create 6 rows of 4 hours each
        for row in range(6):
            button_row: List[InlineKeyboardButton] = []
            for col in range(4):
                hour = row * 4 + col
                button_row.append(InlineKeyboardButton(text=f"{hour:02d}:__", callback_data=f"time_hour:{hour}"))
            buttons.append(button_row)

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def create_minute_keyboard(selected_hour: int) -> InlineKeyboardMarkup:
        """Create inline keyboard for minute selection (0, 15, 30, 45).

        Simplified to 15-minute intervals to reduce button clutter.
        Users can also type exact time if needed.

        Args:
            selected_hour: Hour selected in previous step

        Returns:
            InlineKeyboardMarkup with minute selection buttons
        """
        minutes = [0, 15, 30, 45]
        buttons: List[List[InlineKeyboardButton]] = []

        # Create 2 rows of 2 minutes each
        button_row: List[InlineKeyboardButton] = []
        for minute in minutes:
            button_row.append(
                InlineKeyboardButton(
                    text=f"{selected_hour:02d}:{minute:02d}", callback_data=f"time_minute:{selected_hour}:{minute}"
                )
            )
            # Start new row after 2 buttons
            if len(button_row) == 2:
                buttons.append(button_row)
                button_row = []

        # Add "Enter custom time" option
        buttons.append([InlineKeyboardButton(text="✍️ Enter exact time manually", callback_data="time_manual")])

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    async def handle_hour_selection(callback: CallbackQuery, selected_hour_storage: dict) -> None:
        """Handle hour selection from callback.

        Args:
            callback: Telegram callback query
            selected_hour_storage: Dict to store selected hour (e.g., FSM data or session)
        """
        if not callback.data or not callback.data.startswith("time_hour:"):
            return

        hour = int(callback.data.split(":")[1])
        selected_hour_storage["selected_hour"] = hour

        # Show minute selection keyboard
        if callback.message and not isinstance(callback.message, InaccessibleMessage):
            await callback.message.edit_text(
                f"Hour selected: {hour:02d}\n\nNow select the minute:",
                reply_markup=TimePickerWidget.create_minute_keyboard(hour),
            )
        await callback.answer()

    @staticmethod
    async def handle_minute_selection(callback: CallbackQuery, selected_time_storage: dict) -> Optional[time]:
        """Handle minute selection from callback.

        Args:
            callback: Telegram callback query
            selected_time_storage: Dict to store selected time (e.g., FSM data or session)

        Returns:
            Selected time if valid, None otherwise
        """
        if not callback.data or not callback.data.startswith("time_minute:"):
            return None

        parts = callback.data.split(":")
        hour = int(parts[1])
        minute = int(parts[2])

        # Store selected time
        selected_time = time(hour, minute)
        selected_time_storage["selected_time"] = selected_time
        selected_time_storage["selected_time_display"] = f"{hour:02d}:{minute:02d}"

        await callback.answer(f"Time selected: {hour:02d}:{minute:02d}")

        return selected_time

    @staticmethod
    def get_selected_time(time_storage: dict) -> Optional[time]:
        """Get selected time from storage.

        Args:
            time_storage: Dict containing selected time

        Returns:
            Selected time or None if not yet selected
        """
        return time_storage.get("selected_time")
