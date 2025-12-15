"""Start command handler with menu service integration.

Refactored per T020: Thin wrapper around menu_service with no business logic.
Implements FR-003: Help button shows comprehensive documentation.
"""
https://github.com/azerbaijan-technology/apisbot/pull/12/conflict?name=src%252Fapisbot%252Fbot%252Fstates%252F__init__.py&ancestor_oid=25130e5a6dfd5f1233768b3179eea9cd6d8c74e4&base_oid=e06e42f03053e52222bd6efac65daff31f5ee5f7&head_oid=b6cbbba8437dc6b549074b830dbdb7ccf5d53a2a
import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InaccessibleMessage, InlineKeyboardButton, InlineKeyboardMarkup, Message

from ..states import ChartFlow, CompositeFlow, TransitFlow

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
    """Handle /help command - show usage instructions."""
    logger.info(f"User {message.from_user.id if message.from_user else 'Unknown'}: /help command")

    help_text = (
        "🔮 <b>Natal Chart Bot - Help</b>\n\n"
        "<b>Available Commands:</b>\n"
        "/start - Start generating your natal chart\n"
        "/composite - Create composite chart\n"
        "/transit - Create transit chart\n"
        "/help - Show this help message\n"
        "/cancel - Cancel current operation and clear data\n\n"
        "<b>How it works:</b>\n"
        "1. Send /start to begin\n"
        "2. I'll ask for your name, birth date, time, and location\n"
        "3. I'll generate your personalized natal chart\n"
        "4. You'll receive a beautiful PNG image of your chart\n\n"
        "<b>Date formats:</b>\n"
        "  • YYYY-MM-DD (e.g., 1990-05-15)\n"
        "  • DD/MM/YYYY (e.g., 15/05/1990)\n"
        "  • Month DD, YYYY (e.g., May 15, 1990)\n\n"
        "<b>Time formats:</b>\n"
        "  • 24-hour: HH:MM (e.g., 14:30)\n"
        "  • 12-hour: HH:MM AM/PM (e.g., 2:30 PM)\n"
        "  • Hour only: HH (e.g., 14 or 2 PM)\n\n"
        "<b>Privacy:</b>\n"
        "All your data is deleted immediately after your chart is generated. "
        "We don't store any personal information."
    )

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

    await message.answer(
        "Composite chart\n"
        "I'll need a few pieces of information for 2 subjects:\n"
        "  • Name\n"
        "  • Birth date\n"
        "  • Birth time\n"
        "  • Birth location\n\n"
    )

    await state.set_state(CompositeFlow.waiting_for_name_1)


@router.message(Command("transit"))
async def cmd_transit(message: Message, state: FSMContext):
    """/transit - generate transit chart"""
    logger.info(f"User {message.from_user.id if message.from_user else 'Unknown'}: /composite command")

    await state.clear()

    await message.answer(
        "Transit chart\n"
        "I'll need a few pieces of information for subject and location:\n"
        "  • Name\n"
        "  • Birth date\n"
        "  • Birth time\n"
        "  • Birth location\n\n"
    )

    await state.set_state(TransitFlow.waiting_for_name_1)
