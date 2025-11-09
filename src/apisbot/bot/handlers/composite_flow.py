"""Composite chart flow handlers."""

import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram_dialog import DialogManager, StartMode
from kerykeion import AstrologicalSubjectFactory, KerykeionException

from ...services import ChartService, ConverterService, parse_date, parse_time
from ...services.session_service import get_session_service
from ..dialogs.birth_data_dialog import BirthDataDialog
from ..states import CompositeFlow
from .common import get_state_prompt_with_hints

logger = logging.getLogger(__name__)
router = Router()

# Get session service singleton
session_service = get_session_service()


@router.message(CompositeFlow.waiting_for_name_1)
async def process_name_1(message: Message, state: FSMContext):
    """Handle name input for first subject."""
    if not message.text:
        await message.answer("❌ Please provide a text message with the name.")
        return

    name = message.text.strip()

    # Validate name
    if not name or len(name) < 1 or len(name) > 100:
        await message.answer("❌ Name must be between 1 and 100 characters. Please try again:")
        return

    if not any(c.isalpha() for c in name):
        await message.answer("❌ Name must contain at least one letter. Please try again:")
        return

    logger.info(f"User {message.from_user.id if message.from_user else 'Unknown'}: name_1 validated")

    await state.update_data(name_1=name)
    await state.set_state(CompositeFlow.waiting_for_date_1)
    prompt = get_state_prompt_with_hints(
        "date_entry",
        "Great! 📅\n\nWhat's the birth date of the first person?\n\n"
        "You can either:\n"
        "• Use the calendar picker below ⬇️\n"
        "• Type the date (e.g., '1990-05-15' or 'May 15, 1990')",
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="📅 Open Calendar Picker", callback_data="open_calendar_1")]]
    )

    await message.answer(prompt, reply_markup=keyboard)


@router.callback_query(CompositeFlow.waiting_for_date_1, lambda c: c.data == "open_calendar_1")
async def open_calendar_dialog_1(callback: CallbackQuery, state: FSMContext, dialog_manager: DialogManager):
    """Open calendar dialog for person 1."""
    user_id = callback.from_user.id if callback.from_user else 0
    logger.info(f"User {user_id}: opening calendar dialog for person 1")

    await state.update_data(dialog_for_person=1)
    await dialog_manager.start(BirthDataDialog.selecting_date, mode=StartMode.NORMAL)
    await callback.answer()


@router.message(CompositeFlow.waiting_for_date_1)
async def process_date_1(message: Message, state: FSMContext):
    """Handle birth date input for first subject."""
    if not message.text:
        await message.answer("❌ Please provide a text message with the birth date.")
        return

    date_str = message.text.strip()

    try:
        birth_date = parse_date(date_str)
        logger.info(f"User {message.from_user.id if message.from_user else 'Unknown'}: date_1 validated")

        await state.update_data(birth_date_1=birth_date)
        await state.set_state(CompositeFlow.waiting_for_time_1)
        prompt = get_state_prompt_with_hints(
            "time_entry",
            "Perfect! ⏰\n\nWhat time was the first person born?\n\n" "Type the time (e.g., '14:30' or '2:30 PM')",
        )
        await message.answer(prompt)

    except ValueError as e:
        logger.warning(
            f"User {message.from_user.id if message.from_user else 'Unknown'}: invalid date format for subject 1"
        )
        await message.answer(f"❌ {str(e)}\n\nPlease try again:")


@router.message(CompositeFlow.waiting_for_time_1)
async def process_time_1(message: Message, state: FSMContext):
    """Handle birth time input for first subject."""
    if not message.text:
        await message.answer("❌ Please provide a text message with the birth time.")
        return

    time_str = message.text.strip()

    try:
        birth_time = parse_time(time_str)
        logger.info(f"User {message.from_user.id if message.from_user else 'Unknown'}: time_1 validated")

        await state.update_data(birth_time_1=birth_time)
        await state.set_state(CompositeFlow.waiting_for_location_1)
        prompt = get_state_prompt_with_hints("location_entry", "Excellent! 🌍\n\nWhere was the first person born?")
        await message.answer(prompt)

    except ValueError as e:
        logger.warning(
            f"User {message.from_user.id if message.from_user else 'Unknown'}: invalid time format for subject 1"
        )
        await message.answer(f"❌ {str(e)}\n\nPlease try again:")


@router.message(CompositeFlow.waiting_for_location_1)
async def process_location_1(message: Message, state: FSMContext):
    """Handle birth location input for first subject and move to second subject."""
    if not message.text:
        await message.answer("❌ Please provide a text message with the birth location.")
        return

    location = message.text.strip()

    # Validate location length
    if not location or len(location) < 2 or len(location) > 200:
        await message.answer("❌ Location must be between 2 and 200 characters. Please try again:")
        return

    logger.info(f"User {message.from_user.id if message.from_user else 'Unknown'}: location_1 provided")

    data = await state.get_data()
    try:
        subject_1 = AstrologicalSubjectFactory.from_birth_data(
            name=data["name_1"],
            year=data["birth_date_1"].year,
            month=data["birth_date_1"].month,
            day=data["birth_date_1"].day,
            hour=data["birth_time_1"].hour,
            minute=data["birth_time_1"].minute,
            city=location,
            nation=" ",
        )
    except (ValueError, KerykeionException) as e:
        error_msg = str(e)
        if "city" in error_msg.lower() or "location" in error_msg.lower() or "geonames" in error_msg.lower():
            await state.set_state(CompositeFlow.waiting_for_location_1)
            await message.answer(
                f"❌ <b>Location Error for {data['name_1']} person</b>\n\n"
                f"{error_msg}\n\n"
                "💡 <b>Tips:</b>\n"
                "  • Try adding the country (e.g., 'Paris, France')\n"
                "  • Use a nearby major city if your town isn't found\n"
                "  • Check spelling\n\n"
                f"Please enter the birth location for the {data['name_1']} person again:"
            )
            return
        await message.answer(
            f"❌ <b>Composite Chart Generation Failed</b>\n\n"
            f"{error_msg}\n\n"
            "Please try again from the beginning with /composite"
        )
        return
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Unexpected error occurred: {str(type(e))}")
        await message.answer(
            f"❌ <b>Unexpected Error</b>\n\n" f"{error_msg}\n\n" f"Please try again from the beginning with /composite"
        )
        return

    await state.update_data(location_1=location, subject_1=subject_1)
    await state.set_state(CompositeFlow.waiting_for_name_2)
    await message.answer(
        "✅ First person's data collected!\n\n"
        "Now let's proceed to the second person.\n\n"
        "What's the name of the second person?"
    )


@router.message(CompositeFlow.waiting_for_name_2)
async def process_name_2(message: Message, state: FSMContext):
    """Handle name input for second subject."""
    if not message.text:
        await message.answer("❌ Please provide a text message with the name.")
        return

    name = message.text.strip()

    # Validate name
    if not name or len(name) < 1 or len(name) > 100:
        await message.answer("❌ Name must be between 1 and 100 characters. Please try again:")
        return

    if not any(c.isalpha() for c in name):
        await message.answer("❌ Name must contain at least one letter. Please try again:")
        return

    logger.info(f"User {message.from_user.id if message.from_user else 'Unknown'}: name_2 validated")

    # Store name for second subject
    await state.update_data(name_2=name)

    # Move to next state for second subject
    await state.set_state(CompositeFlow.waiting_for_date_2)

    # Use menu_service for state hints (T021) with calendar widget option
    prompt = get_state_prompt_with_hints(
        "date_entry",
        "Great! 📅\n\nWhat's the birth date of the second person?\n\n"
        "You can either:\n"
        "• Use the calendar picker below ⬇️\n"
        "• Type the date (e.g., '1990-05-15' or 'May 15, 1990')",
    )

    # Create inline keyboard with calendar option
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="📅 Open Calendar Picker", callback_data="open_calendar_2")]]
    )

    await message.answer(prompt, reply_markup=keyboard)


@router.callback_query(CompositeFlow.waiting_for_date_2, lambda c: c.data == "open_calendar_2")
async def open_calendar_dialog_2(callback: CallbackQuery, state: FSMContext, dialog_manager: DialogManager):
    """Open calendar dialog for person 2 date and time selection.

    Implements T039: Calendar widget integration for composite flow person 2.
    """
    user_id = callback.from_user.id if callback.from_user else 0
    logger.info(f"User {user_id}: opening calendar dialog for person 2")

    # Store person indicator
    await state.update_data(dialog_for_person=2)

    # Start the birth data dialog (calendar + time picker)
    await dialog_manager.start(BirthDataDialog.selecting_date, mode=StartMode.NORMAL)
    await callback.answer()


@router.message(CompositeFlow.waiting_for_date_2)
async def process_date_2(message: Message, state: FSMContext):
    """Handle birth date input for second subject."""
    if not message.text:
        await message.answer("❌ Please provide a text message with the birth date.")
        return

    date_str = message.text.strip()

    try:
        birth_date = parse_date(date_str)
        logger.info(f"User {message.from_user.id if message.from_user else 'Unknown'}: date_2 validated")

        # Store date for second subject
        await state.update_data(birth_date_2=birth_date)

        # Move to next state
        await state.set_state(CompositeFlow.waiting_for_time_2)

        # Use menu_service for state hints (T021)
        prompt = get_state_prompt_with_hints(
            "time_entry",
            "Perfect! ⏰\n\nWhat time was the second person born?\n\n" "Type the time (e.g., '14:30' or '2:30 PM')",
        )
        await message.answer(prompt)

    except ValueError as e:
        logger.warning(
            f"User {message.from_user.id if message.from_user else 'Unknown'}: invalid date format for subject 2"
        )
        await message.answer(f"❌ {str(e)}\n\nPlease try again:")


@router.message(CompositeFlow.waiting_for_time_2)
async def process_time_2(message: Message, state: FSMContext):
    """Handle birth time input for second subject."""
    if not message.text:
        await message.answer("❌ Please provide a text message with the birth time.")
        return

    time_str = message.text.strip()

    try:
        birth_time = parse_time(time_str)
        logger.info(f"User {message.from_user.id if message.from_user else 'Unknown'}: time_2 validated")

        # Store time for second subject
        await state.update_data(birth_time_2=birth_time)

        # Move to next state
        await state.set_state(CompositeFlow.waiting_for_location_2)

        # Use menu_service for state hints (T021)
        prompt = get_state_prompt_with_hints("location_entry", "Excellent! 🌍\n\nWhere was the second person born?")
        await message.answer(prompt)

    except ValueError as e:
        logger.warning(
            f"User {message.from_user.id if message.from_user else 'Unknown'}: invalid time format for subject 2"
        )
        await message.answer(f"❌ {str(e)}\n\nPlease try again:")


@router.message(CompositeFlow.waiting_for_location_2)
async def process_location_2(message: Message, state: FSMContext):
    """Handle birth location input and generate composite chart."""
    if not message.text:
        await message.answer("❌ Please provide a text message with the birth location.")
        return

    location = message.text.strip()

    # Validate location length
    if not location or len(location) < 2 or len(location) > 200:
        await message.answer("❌ Location must be between 2 and 200 characters. Please try again:")
        return

    logger.info(f"User {message.from_user.id if message.from_user else 'Unknown'}: location_2 provided")

    # Store location for second subject
    await state.update_data(location_2=location)

    # Move to generating state
    await state.set_state(CompositeFlow.generating_composite_chart)

    # Show progress message
    progress_msg = await message.answer(
        "⏳ Generating your composite chart...\n\n" "This may take a few seconds. Please wait."
    )

    try:
        # Get all stored data
        data = await state.get_data()

        subject_1 = data["subject_1"]

        subject_2 = AstrologicalSubjectFactory.from_birth_data(
            name=data["name_2"],
            year=data["birth_date_2"].year,
            month=data["birth_date_2"].month,
            day=data["birth_date_2"].day,
            hour=data["birth_time_2"].hour,
            minute=data["birth_time_2"].minute,
            city=location,
            nation=" ",
        )

        # Generate composite chart
        chart_service = ChartService()
        svg_chart = await chart_service.generate_composite(subject_1, subject_2)

        logger.info(
            f"User {message.from_user.id if message.from_user else 'Unknown'}: composite chart generated successfully"
        )

        # Convert to PNG
        converter_service = ConverterService()
        png_bytes = await converter_service.svg_to_png(svg_chart)

        logger.info(
            f"User {message.from_user.id if message.from_user else 'Unknown'}: composite chart converted to PNG"
        )

        # Send chart to user
        chart_file = BufferedInputFile(png_bytes, filename="composite_chart.png")
        await message.answer_photo(
            photo=chart_file,
            caption=(
                f"✨ <b>Composite Chart</b> ✨\n\n"
                f"Between {subject_1.name} and {subject_2.name}\n\n"
                f"<b>First person:</b>\n"
                f"Born: {data['birth_date_1'].strftime('%B %d, %Y')} "
                f"at {data['birth_date_1'].strftime('%H:%M')}\n"
                f"Location: {subject_1.city}\n\n"
                f"<b>Second person:</b>\n"
                f"Born: {data['birth_date_2'].strftime('%B %d, %Y')} "
                f"at {data['birth_time_2'].strftime('%H:%M')}\n"
                f"Location: {subject_2.city}\n\n"
                "All your data has been securely deleted. 🔒\n\n"
                "Want to generate another chart? Send /start or /composite"
            ),
        )

        # Delete progress message
        await progress_msg.delete()

        # Clear state and all data (privacy)
        await state.clear()

        logger.info(
            f"User {message.from_user.id if message.from_user else 'Unknown'}: composite chart delivered, data cleared"
        )

    except (ValueError, KerykeionException) as e:
        logger.error(
            f"User {message.from_user.id if message.from_user else 'Unknown'}: "
            f"composite chart generation failed - {str(e)}"
        )

        # Delete progress message
        await progress_msg.delete()

        # Show error with helpful message
        error_msg = str(e)

        if "location" in error_msg.lower() or "city" in error_msg.lower() or "geonames" in error_msg.lower():
            # Determine which subject has the location error
            if "first" in error_msg.lower():
                subject = "first"
            else:
                subject = "second"

            await message.answer(
                f"❌ <b>Location Error for {subject} person</b>\n\n"
                f"{error_msg}\n\n"
                "💡 <b>Tips:</b>\n"
                "  • Try adding the country (e.g., 'Paris, France')\n"
                "  • Use a nearby major city if your town isn't found\n"
                "  • Check spelling\n\n"
                f"Please enter the birth location for the {subject} person again:"
            )
            # Go back to appropriate location state
            if subject == "first":
                await state.set_state(CompositeFlow.waiting_for_location_1)
            else:
                await state.set_state(CompositeFlow.waiting_for_location_2)
        else:
            await message.answer(
                f"❌ <b>Composite Chart Generation Failed</b>\n\n"
                f"{error_msg}\n\n"
                "Please try again from the beginning with /composite"
            )
            await state.clear()

    except Exception:
        logger.exception(
            f"User {message.from_user.id if message.from_user else 'Unknown'}: "
            "unexpected error during composite chart generation"
        )

        # Delete progress message
        try:
            await progress_msg.delete()
        except Exception:
            pass

        await message.answer(
            "❌ <b>Unexpected Error</b>\n\n"
            "Something went wrong while generating your composite chart. "
            "Please try again with /composite\n\n"
            "If the problem persists, contact support."
        )
        await state.clear()
