import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, Message

from ...models import BirthData
from ...services import ChartService, ConverterService, parse_date, parse_time
from ..states import ChartFlow

logger = logging.getLogger(__name__)
router = Router()


@router.message(ChartFlow.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    """Handle name input during chart flow."""
    if not message.text:
        await message.answer("❌ Please provide a text message with your name.")
        return

    name = message.text.strip()

    # Validate name
    if not name or len(name) < 1 or len(name) > 100:
        await message.answer("❌ Name must be between 1 and 100 characters. Please try again:")
        return

    if not any(c.isalpha() for c in name):
        await message.answer("❌ Name must contain at least one letter. Please try again:")
        return

    logger.info(f"User {message.from_user.id if message.from_user else 'Unknown'}: name validated")

    # Store name
    await state.update_data(name=name)

    # Move to next state
    await state.set_state(ChartFlow.waiting_for_date)
    await message.answer(
        f"Great, {name}! 📅\n\n"
        "What's your birth date?\n\n"
        "You can use any of these formats:\n"
        "  • YYYY-MM-DD (e.g., 1990-05-15)\n"
        "  • DD/MM/YYYY (e.g., 15/05/1990)\n"
        "  • Month DD, YYYY (e.g., May 15, 1990)"
    )


@router.message(ChartFlow.waiting_for_date)
async def process_date(message: Message, state: FSMContext):
    """Handle birth date input during chart flow."""
    if not message.text:
        await message.answer("❌ Please provide a text message with your birth date.")
        return

    date_str = message.text.strip()

    try:
        birth_date = parse_date(date_str)
        logger.info(f"User {message.from_user.id if message.from_user else 'Unknown'}: date validated")

        # Store date
        await state.update_data(birth_date=birth_date)

        # Move to next state
        await state.set_state(ChartFlow.waiting_for_time)
        await message.answer(
            "Perfect! ⏰\n\n"
            "What time were you born?\n\n"
            "You can use any of these formats:\n"
            "  • 24-hour: HH:MM (e.g., 14:30)\n"
            "  • 12-hour: HH:MM AM/PM (e.g., 2:30 PM)\n"
            "  • Hour only: HH (e.g., 14 or 2 PM)"
        )

    except ValueError as e:
        logger.warning(f"User {message.from_user.id if message.from_user else 'Unknown'}: invalid date format")
        await message.answer(f"❌ {str(e)}\n\nPlease try again:")


@router.message(ChartFlow.waiting_for_time)
async def process_time(message: Message, state: FSMContext):
    """Handle birth time input during chart flow."""
    if not message.text:
        await message.answer("❌ Please provide a text message with your birth time.")
        return

    time_str = message.text.strip()

    try:
        birth_time = parse_time(time_str)
        logger.info(f"User {message.from_user.id if message.from_user else 'Unknown'}: time validated")

        # Store time
        await state.update_data(birth_time=birth_time)

        # Move to next state
        await state.set_state(ChartFlow.waiting_for_location)
        await message.answer(
            "Excellent! 🌍\n\n"
            "Finally, where were you born?\n\n"
            "Please provide a city name (e.g., 'New York, USA' or 'London, UK').\n"
            "Be as specific as possible for accurate results."
        )

    except ValueError as e:
        logger.warning(f"User {message.from_user.id if message.from_user else 'Unknown'}: invalid time format")
        await message.answer(f"❌ {str(e)}\n\nPlease try again:")


@router.message(ChartFlow.waiting_for_location)
async def process_location(message: Message, state: FSMContext):
    """Handle birth location input and generate chart."""
    if not message.text:
        await message.answer("❌ Please provide a text message with your birth location.")
        return

    location = message.text.strip()

    # Validate location length
    if not location or len(location) < 2 or len(location) > 200:
        await message.answer("❌ Location must be between 2 and 200 characters. Please try again:")
        return

    logger.info(f"User {message.from_user.id if message.from_user else 'Unknown'}: location provided")

    # Store location
    await state.update_data(location=location)

    # Move to generating state
    await state.set_state(ChartFlow.generating_chart)

    # Show progress message
    progress_msg = await message.answer(
        "⏳ Generating your natal chart...\n\n" "This may take a few seconds. Please wait."
    )

    try:
        # Get all stored data
        data = await state.get_data()

        # Create BirthData object
        birth_data = BirthData(
            name=data["name"],
            birth_date=data["birth_date"],
            birth_time=data["birth_time"],
            location=location,
            nation=" ",
        )

        # Generate chart
        chart_service = ChartService()
        svg_chart = await chart_service.generate_chart(birth_data)

        logger.info(f"User {message.from_user.id if message.from_user else 'Unknown'}: chart generated successfully")

        # Convert to PNG
        converter_service = ConverterService()
        png_bytes = await converter_service.svg_to_png(svg_chart)

        logger.info(f"User {message.from_user.id if message.from_user else 'Unknown'}: chart converted to PNG")

        # Send chart to user
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

        # Delete progress message
        await progress_msg.delete()

        # Clear state and all data (privacy)
        await state.clear()

        logger.info(f"User {message.from_user.id if message.from_user else 'Unknown'}: chart delivered, data cleared")

    except ValueError as e:
        logger.error(
            f"User {message.from_user.id if message.from_user else 'Unknown'}: chart generation failed - {str(e)}"
        )

        # Delete progress message
        await progress_msg.delete()

        # Show error with helpful message
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
            # Go back to location state
            await state.set_state(ChartFlow.waiting_for_location)
        else:
            await message.answer(
                f"❌ <b>Chart Generation Failed</b>\n\n"
                f"{error_msg}\n\n"
                "Please try again from the beginning with /start"
            )
            await state.clear()

    except Exception:
        logger.exception(
            f"User {message.from_user.id if message.from_user else 'Unknown'}: unexpected error during chart generation"
        )

        # Delete progress message
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
