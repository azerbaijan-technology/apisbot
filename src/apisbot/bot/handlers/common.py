"""Common helper functions for handlers.

Framework-agnostic utilities for enhancing handler responses with command hints.
Implements T021: Add command hints to state handlers using menu_service.
"""

from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ...services.menu_service import MenuService


def get_command_hints(state: str) -> str:
    """Get formatted command hints for the current state.

    This is a thin wrapper around MenuService.get_state_hints() that
    formats the hints as a user-friendly string.

    Args:
        state: Current FSM state name (e.g., 'date_entry', 'time_entry')

    Returns:
        Formatted hint text ready to append to messages

    Example:
        >>> hints = get_command_hints('date_entry')
        >>> message_text = f"Enter your birth date\\n\\n{hints}"
    """
    hints = MenuService.get_state_hints(state)
    if not hints:
        return ""

    return "\n".join([f"💡 {hint}" for hint in hints])


def create_hint_keyboard(state: str, include_cancel: bool = True) -> InlineKeyboardMarkup:
    """Create inline keyboard with command hint buttons.

    Creates a keyboard with helpful action buttons based on the current state.
    Always includes help and optionally includes cancel.

    Args:
        state: Current FSM state name
        include_cancel: Whether to include a cancel button (default: True)

    Returns:
        InlineKeyboardMarkup with hint buttons

    Example:
        >>> keyboard = create_hint_keyboard('date_entry', include_cancel=True)
        >>> await message.answer("Enter date:", reply_markup=keyboard)
    """
    buttons: List[List[InlineKeyboardButton]] = []

    # Add help button (always present)
    buttons.append([InlineKeyboardButton(text="❓ Help", callback_data="show_help")])

    # Add cancel button (usually present)
    if include_cancel:
        buttons.append([InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_flow")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_state_prompt_with_hints(state: str, prompt_text: str) -> str:
    """Combine a prompt with contextual command hints.

    Appends formatted command hints to a user-facing prompt message.

    Args:
        state: Current FSM state name
        prompt_text: The main prompt to show the user

    Returns:
        Combined prompt text with hints appended

    Example:
        >>> text = get_state_prompt_with_hints(
        ...     'date_entry',
        ...     "What's your birth date?"
        ... )
        >>> await message.answer(text)
    """
    hints = get_command_hints(state)
    if hints:
        return f"{prompt_text}\n\n{hints}"
    return prompt_text
