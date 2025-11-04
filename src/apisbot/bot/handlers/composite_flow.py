import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, Message

from ...models import BirthData
from ...services import ChartService, ConverterService, parse_date, parse_time
from ..states import CompositeFlow

logger = logging.getLogger(__name__)
router = Router()


# Первый субъект
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

    # Store name for first subject
    await state.update_data(name_1=name)

    # Move to next state for first subject
    await state.set_state(CompositeFlow.waiting_for_date_1)
    await message.answer(
        "Great! 📅\n\n"
        "What's the birth date of the first person?\n\n"
        "You can use any of these formats:\n"
        "  • YYYY-MM-DD (e.g., 1990-05-15)\n"
        "  • DD/MM/YYYY (e.g., 15/05/1990)\n"
        "  • Month DD, YYYY (e.g., May 15, 1990)"
    )


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

        # Store date for first subject
        await state.update_data(birth_date_1=birth_date)

        # Move to next state
        await state.set_state(CompositeFlow.waiting_for_time_1)
        await message.answer(
            "Perfect! ⏰\n\n"
            "What time was the first person born?\n\n"
            "You can use any of these formats:\n"
            "  • 24-hour: HH:MM (e.g., 14:30)\n"
            "  • 12-hour: HH:MM AM/PM (e.g., 2:30 PM)\n"
            "  • Hour only: HH (e.g., 14 or 2 PM)"
        )

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

        # Store time for first subject
        await state.update_data(birth_time_1=birth_time)

        # Move to next state
        await state.set_state(CompositeFlow.waiting_for_location_1)
        await message.answer(
            "Excellent! 🌍\n\n"
            "Where was the first person born?\n\n"
            "Please provide a city name (e.g., 'New York, USA' or 'London, UK').\n"
            "Be as specific as possible for accurate results."
        )

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

    # Store location for first subject
    await state.update_data(location_1=location)

    # Move to second subject
    await state.set_state(CompositeFlow.waiting_for_name_2)
    await message.answer(
        "✅ First person's data collected!\n\n"
        "Now let's proceed to the second person.\n\n"
        "What's the name of the second person?"
    )


# Второй субъект (повторяем тот же flow)
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
    await message.answer(
        "Great! 📅\n\n"
        "What's the birth date of the second person?\n\n"
        "You can use any of these formats:\n"
        "  • YYYY-MM-DD (e.g., 1990-05-15)\n"
        "  • DD/MM/YYYY (e.g., 15/05/1990)\n"
        "  • Month DD, YYYY (e.g., May 15, 1990)"
    )


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
        await message.answer(
            "Perfect! ⏰\n\n"
            "What time was the second person born?\n\n"
            "You can use any of these formats:\n"
            "  • 24-hour: HH:MM (e.g., 14:30)\n"
            "  • 12-hour: HH:MM AM/PM (e.g., 2:30 PM)\n"
            "  • Hour only: HH (e.g., 14 or 2 PM)"
        )

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
        await message.answer(
            "Excellent! 🌍\n\n"
            "Where was the second person born?\n\n"
            "Please provide a city name (e.g., 'New York, USA' or 'London, UK').\n"
            "Be as specific as possible for accurate results."
        )

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

        # Create BirthData objects for both subjects
        birth_data_1 = BirthData(
            name=data["name_1"],
            birth_date=data["birth_date_1"],
            birth_time=data["birth_time_1"],
            location=data["location_1"],
        )

        birth_data_2 = BirthData(
            name=data["name_2"],
            birth_date=data["birth_date_2"],
            birth_time=data["birth_time_2"],
            location=data["location_2"],
        )

        # Generate composite chart
        chart_service = ChartService()
        svg_chart = await chart_service.generate_composite(birth_data_1, birth_data_2)

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
                f"Between {birth_data_1.name} and {birth_data_2.name}\n\n"
                f"<b>First person:</b>\n"
                f"Born: {birth_data_1.birth_date.strftime('%B %d, %Y')} "
                f"at {birth_data_1.birth_time.strftime('%H:%M')}\n"
                f"Location: {birth_data_1.location}\n\n"
                f"<b>Second person:</b>\n"
                f"Born: {birth_data_2.birth_date.strftime('%B %d, %Y')} "
                f"at {birth_data_2.birth_time.strftime('%H:%M')}\n"
                f"Location: {birth_data_2.location}\n\n"
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

    except ValueError as e:
        logger.error(
            f"User {message.from_user.id if message.from_user else 'Unknown'}: "
            f"composite chart generation failed - {str(e)}"
        )

        # Delete progress message
        await progress_msg.delete()

        # Show error with helpful message
        error_msg = str(e)

        if "location" in error_msg.lower() or "city" in error_msg.lower():
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
