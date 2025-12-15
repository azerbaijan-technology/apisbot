"""Start command handler with menu service integration.

Refactored per T020: Thin wrapper around menu_service with no business logic.
Implements FR-003: Help button shows comprehensive documentation.
"""

import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InaccessibleMessage, InlineKeyboardButton, InlineKeyboardMarkup, Message

from ...models.chart_selection import ChartSelection
from ...models.errors import ValidationError
from ...services.chart_selection_service import ChartSelectionService
from ...services.menu_service import MenuService
from ...services.session_service import get_session_service
from ..states import ChartFlow
from ..states import ChartSelection as ChartSelectionState
from ..states import CompositeFlow

logger = logging.getLogger(__name__)
router = Router()

# Get session service singleton
session_service = get_session_service()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command - display chart selection menu.

    Refactored per T020: Uses menu_service for all text generation.
    Implements US2: Interactive chart selection menu.
    """
    user_id = message.from_user.id if message.from_user else 0
    logger.info(f"User {user_id}: /start command")

    # Clear any existing state and session
    await state.clear()
    if user_id:
        await session_service.clear_session(user_id)

    # Get menu text from service (no business logic in handler)
    menu_text = MenuService.get_start_menu_text()

    # Create inline keyboard with chart selection buttons
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"🔮 {ChartSelection.NATAL.display_name}",
                    callback_data=f"chart_select:{ChartSelection.NATAL.value}",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"💑 {ChartSelection.COMPOSITE.display_name}",
                    callback_data=f"chart_select:{ChartSelection.COMPOSITE.value}",
                )
            ],
            [InlineKeyboardButton(text="❓ Help", callback_data="show_help")],
        ]
    )

    # Set FSM state to chart selection (T026)
    await state.set_state(ChartSelectionState.selecting_chart)

    await message.answer(menu_text, reply_markup=keyboard)


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command - show comprehensive help documentation.

    Refactored per T020: Uses menu_service.get_help_documentation().
    Implements FR-003: Help button shows comprehensive documentation.
    """
    user_id = message.from_user.id if message.from_user else 0
    logger.info(f"User {user_id}: /help command")

    # Get help documentation from service (no business logic in handler)
    help_text = MenuService.get_help_documentation()

    await message.answer(help_text)


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Handle /cancel command - clear FSM state and session data.

    Privacy-first: Ensures all user data is cleared from session storage.
    """
    user_id = message.from_user.id if message.from_user else 0
    logger.info(f"User {user_id}: /cancel command")

    current_state = await state.get_state()

    if current_state is None:
        await message.answer("Nothing to cancel. Send /start to begin generating your chart.")
    else:
        # Clear FSM state
        await state.clear()

        # Clear session data (privacy-first)
        if user_id:
            await session_service.clear_session(user_id)

        await message.answer(
            "❌ Operation cancelled. All your data has been cleared.\n\n"
            "Send /start whenever you're ready to try again."
        )


# Callback handlers for chart selection (T025)
@router.callback_query(F.data.startswith("chart_select:"))
async def handle_chart_selection(callback: CallbackQuery, state: FSMContext):
    """Handle chart type selection from inline buttons.

    Implements T025: Route button clicks to appropriate flow (natal_flow or composite_flow).
    Uses chart_selection_service for validation.
    """
    user_id = callback.from_user.id if callback.from_user else 0

    if not callback.data:
        await callback.answer("Invalid selection")
        return

    # Extract chart type from callback data
    chart_type_str = callback.data.split(":")[1]

    # Validate using service
    result = await ChartSelectionService.select_chart(user_id, chart_type_str)

    if isinstance(result, ValidationError):
        await callback.answer(str(result.message), show_alert=True)
        return

    chart_type = result

    # Store chart type in session
    session = await session_service.get_or_create_session(user_id)
    session.chart_type = chart_type

    # Route to appropriate flow
    if chart_type == ChartSelection.NATAL:
        if callback.message and not isinstance(callback.message, InaccessibleMessage):
            await callback.message.edit_text(
                f"✅ {ChartSelection.NATAL.display_name} selected!\n\n"
                "I'll need the following information:\n"
                "  • Name\n"
                "  • Birth date\n"
                "  • Birth time\n"
                "  • Birth location\n\n"
                "Let's get started! What's your name?"
            )
        await state.set_state(ChartFlow.waiting_for_name)

    elif chart_type == ChartSelection.COMPOSITE:
        if callback.message and not isinstance(callback.message, InaccessibleMessage):
            await callback.message.edit_text(
                f"✅ {ChartSelection.COMPOSITE.display_name} selected!\n\n"
                "I'll need information for two people:\n\n"
                "**Person 1:**\n"
                "  • Name\n"
                "  • Birth date\n"
                "  • Birth time\n"
                "  • Birth location\n\n"
                "**Person 2:** (same information)\n\n"
                "Let's start with Person 1. What's their name?"
            )
        await state.set_state(CompositeFlow.waiting_for_name_1)

    await callback.answer()


@router.callback_query(F.data == "show_help")
async def handle_help_button(callback: CallbackQuery):
    """Handle help button click from chart selection menu.

    Implements FR-003: Help button shows comprehensive documentation.
    """
    user_id = callback.from_user.id if callback.from_user else 0
    logger.info(f"User {user_id}: Help button clicked")

    # Get help text from service
    help_text = MenuService.get_help_documentation()

    # Send help text and re-show menu
    if callback.message:
        await callback.message.answer(help_text)
    await callback.answer("Help sent! Scroll up to read it.")
