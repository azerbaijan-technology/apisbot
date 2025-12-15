"""Natal chart flow handlers."""

import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram_dialog import DialogManager, StartMode

from ...models import BirthData
from ...models.errors import ValidationError
from ...services import ChartService, ConverterService, InputValidationService
from ...services.session_service import get_session_service
from ..dialogs.birth_data_dialog import BirthDataDialog
from ..states import ChartFlow
from ..widgets.time_picker import TimePickerWidget
from .common import get_state_prompt_with_hints

logger = logging.getLogger(__name__)
router = Router()

# Get session service singleton
session_service = get_session_service()


@router.message(ChartFlow.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    """Handle name input."""
    user_id = message.from_user.id if message.from_user else 0

    if not message.text:
        await message.answer("❌ Please provide a text message with your name.")
        return

    result = InputValidationService.validate_name(message.text)

    if isinstance(result, ValidationError):
        await message.answer(f"❌ {result}")
        return

    validated_name = result
    logger.info(f"User {user_id}: name validated")

    await state.update_data(name=validated_name)
    await state.set_state(ChartFlow.waiting_for_date)
    prompt = get_state_prompt_with_hints(
        "date_entry",
        f"Great, {validated_name}! 📅\n\nWhat's your birth date?\n\n"
        "You can either:\n"
        "• Use the calendar picker below ⬇️\n"
        "• Type the date (e.g., '1990-05-15' or 'May 15, 1990')",
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="📅 Open Calendar Picker", callback_data="open_calendar")]]
    )

    await message.answer(prompt, reply_markup=keyboard)


@router.callback_query(ChartFlow.waiting_for_date, lambda c: c.data == "open_calendar")
async def open_calendar_dialog(callback: CallbackQuery, state: FSMContext, dialog_manager: DialogManager):
    """Open calendar dialog for date and time selection."""
    user_id = callback.from_user.id if callback.from_user else 0
    logger.info(f"User {user_id}: opening calendar dialog")

    await dialog_manager.start(BirthDataDialog.selecting_date, mode=StartMode.NORMAL)
    await callback.answer()


@router.message(ChartFlow.waiting_for_date)
async def process_date(message: Message, state: FSMContext):
    """Handle birth date input."""
    user_id = message.from_user.id if message.from_user else 0

    if not message.text:
        await message.answer("❌ Please provide a text message with your birth date.")
        return

    result = await InputValidationService.validate_date(message.text)

    if isinstance(result, ValidationError):
        await message.answer(f"❌ {result}")
        return

    date_data = result
    logger.info(f"User {user_id}: date validated")

    await state.update_data(birth_date=date_data.birth_date)
    await state.set_state(ChartFlow.waiting_for_time)
    prompt = get_state_prompt_with_hints(
        "time_entry",
        "Perfect! ⏰\n\nWhat time were you born?\n\n" "Type the time (e.g., '14:30' or '2:30 PM')",
    )
    await message.answer(prompt)


@router.callback_query(ChartFlow.waiting_for_time, lambda c: c.data and c.data.startswith("time_hour:"))
async def process_time_hour_selection(callback: CallbackQuery, state: FSMContext):
    """Handle hour selection from time picker widget."""
    user_id = callback.from_user.id if callback.from_user else 0

    data = await state.get_data()
    await TimePickerWidget.handle_hour_selection(callback, data)
    await state.update_data(**data)

    logger.info(f"User {user_id}: hour selected via time picker")


@router.callback_query(ChartFlow.waiting_for_time, lambda c: c.data and c.data.startswith("time_minute:"))
async def process_time_minute_selection(callback: CallbackQuery, state: FSMContext):
    """Handle minute selection from time picker widget."""
    user_id = callback.from_user.id if callback.from_user else 0

    data = await state.get_data()
    selected_time = await TimePickerWidget.handle_minute_selection(callback, data)

    if selected_time:
        await state.update_data(birth_time=selected_time)
        logger.info(f"User {user_id}: time selected via time picker - {selected_time}")

        await state.set_state(ChartFlow.waiting_for_location)

        prompt = get_state_prompt_with_hints("location_entry", "Excellent! 🌍\n\nFinally, where were you born?")

        if callback.message and not isinstance(callback.message, __import__("aiogram.types").InaccessibleMessage):
            await callback.message.answer(prompt)


@router.callback_query(ChartFlow.waiting_for_time, lambda c: c.data == "time_manual")
async def process_time_manual_entry(callback: CallbackQuery, state: FSMContext):
    """Handle manual time entry option from time picker."""
    user_id = callback.from_user.id if callback.from_user else 0

    logger.info(f"User {user_id}: chose manual time entry")

    prompt = get_state_prompt_with_hints(
        "time_entry", "⏰ Please type your birth time\n\n" "Examples: '14:30', '2:30 PM', '09:15'"
    )

    from aiogram.types import InaccessibleMessage

    if callback.message and not isinstance(callback.message, InaccessibleMessage):
        await callback.message.edit_text(prompt)

    await callback.answer()


@router.message(ChartFlow.waiting_for_time)
async def process_time(message: Message, state: FSMContext):
    """Handle birth time text input."""
    user_id = message.from_user.id if message.from_user else 0

    if not message.text:
        await message.answer("❌ Please provide a text message with your birth time.")
        return

    result = await InputValidationService.validate_time(message.text)

    if isinstance(result, ValidationError):
        await message.answer(f"❌ {result}")
        return

    time_data = result
    logger.info(f"User {user_id}: time validated (text input)")

    await state.update_data(birth_time=time_data.birth_time)
    await state.set_state(ChartFlow.waiting_for_location)
    prompt = get_state_prompt_with_hints("location_entry", "Excellent! 🌍\n\nFinally, where were you born?")
    await message.answer(prompt)


@router.message(ChartFlow.waiting_for_location)
async def process_location(message: Message, state: FSMContext):
    """Handle birth location input and generate chart."""
    user_id = message.from_user.id if message.from_user else 0

    if not message.text:
        await message.answer("❌ Please provide a text message with your birth location.")
        return

    result = await InputValidationService.validate_location(message.text)

    if isinstance(result, ValidationError):
        await message.answer(f"❌ {result}")
        return

    location_data = result
    logger.info(f"User {user_id}: location validated and geocoded")

    await state.set_state(ChartFlow.generating_chart)
    progress_msg = await message.answer(
        "⏳ Generating your natal chart...\n\n" "This may take a few seconds. Please wait."
    )

    try:
        data = await state.get_data()
        birth_data = BirthData(
            name=data["name"],
            birth_date=data["birth_date"],
            birth_time=data["birth_time"],
            location=location_data.city,
            latitude=location_data.latitude,
            longitude=location_data.longitude,
            timezone=location_data.timezone,
            nation=" ",
        )

        chart_service = ChartService()
        svg_chart = await chart_service.generate_chart(birth_data)

        logger.info(f"User {user_id}: chart generated successfully")

        converter_service = ConverterService()
        png_bytes = await converter_service.svg_to_png(svg_chart)

        logger.info(f"User {user_id}: chart converted to PNG")
        chart_file = BufferedInputFile(png_bytes, filename="natal_chart.png")
        await message.answer_photo(
            photo=chart_file,
            caption=(
                f"✨ <b>Your Natal Chart</b> ✨\n\n"
                f"Generated for {birth_data.name}\n"
                f"Born: {birth_data.birth_date.strftime('%B %d, %Y')} "
                f"at {birth_data.birth_time.strftime('%H:%M')}\n"
                f"Location: {birth_data.location}\n\n"
                "All your data has been securely deleted. 🔒\n\n"
                "Want to generate another chart? Send /start"
            ),
        )

        await progress_msg.delete()
        await state.clear()

        if user_id:
            await session_service.clear_session(user_id)

        logger.info(f"User {user_id}: chart delivered, all data cleared")

    except ValueError as e:
        logger.error(f"User {user_id}: chart generation failed - {str(e)}")

        await progress_msg.delete()

        error_msg = str(e)

        if "location" in error_msg.lower() or "city" in error_msg.lower():
            await message.answer(
                f"❌ <b>Location Error</b>\n\n"
                f"{error_msg}\n\n"
                "💡 <b>Tips:</b>\n"
                "  • Try adding the country (e.g., 'Paris, France')\n"
                "  • Use a nearby major city if your town isn't found\n"
                "  • Check spelling\n\n"
                "Please enter your birth location again:"
            )
            await state.set_state(ChartFlow.waiting_for_location)
        else:
            await message.answer(
                f"❌ <b>Chart Generation Failed</b>\n\n"
                f"{error_msg}\n\n"
                "Please try again from the beginning with /start"
            )
            await state.clear()
            if user_id:
                await session_service.clear_session(user_id)

    except Exception:
        logger.exception(f"User {user_id}: unexpected error during chart generation")

        try:
            await progress_msg.delete()
        except Exception:
            pass

        await message.answer(
            "❌ <b>Unexpected Error</b>\n\n"
            "Something went wrong while generating your chart. "
            "Please try again with /start\n\n"
            "If the problem persists, contact support."
        )
        await state.clear()
        if user_id:
            await session_service.clear_session(user_id)
