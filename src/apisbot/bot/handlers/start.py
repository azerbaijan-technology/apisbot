import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from ..states import ChartFlow, CompositeFlow, TransitFlow

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command - begin chart generation flow.

    Clears any existing state and starts the conversation.
    """
    logger.info(f"User {message.from_user.id if message.from_user else 'Unknown'}: /start command")

    # Clear any existing state
    await state.clear()

    # Welcome message
    await message.answer(
        "👋 Welcome to the Natal Chart Bot!\n\n"
        "I'll help you generate your personalized natal chart. "
        "I'll need a few pieces of information:\n"
        "  • Your name\n"
        "  • Your birth date\n"
        "  • Your birth time\n"
        "  • Your birth location\n\n"
        "Let's get started! What's your name?"
    )

    # Set state to waiting for name
    await state.set_state(ChartFlow.waiting_for_name)


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
    """Handle /cancel command - clear FSM state and cancel current operation."""
    logger.info(f"User {message.from_user.id if message.from_user else 'Unknown'}: /cancel command")

    current_state = await state.get_state()

    if current_state is None:
        await message.answer("Nothing to cancel. Send /start to begin generating your natal chart.")
    else:
        await state.clear()
        await message.answer(
            "❌ Operation cancelled. All your data has been cleared.\n\n"
            "Send /start whenever you're ready to try again."
        )


@router.message(Command("composite"))
async def cmd_composite(message: Message, state: FSMContext):
    """/composite - generate composite chart between 2 subjects"""
    logger.info(f"User {message.from_user.id if message.from_user else 'Unknown'}: /composite command")

    await state.clear()

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
