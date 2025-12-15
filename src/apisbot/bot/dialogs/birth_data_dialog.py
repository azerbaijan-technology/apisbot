"""Birth data collection dialog with calendar and time picker widgets.

Implements T037: Calendar widget integration for date selection.
Implements T038: Time picker widget integration for time selection.
"""

from datetime import date, time
from typing import Any, Dict

from aiogram.fsm.state import State, StatesGroup
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Calendar, Row, Select
from aiogram_dialog.widgets.kbd.calendar_kbd import CalendarConfig
from aiogram_dialog.widgets.text import Const, Format

from ...services.input_validation_service import InputValidationService
from ..states import ChartFlow, CompositeFlow

# Calendar configuration for birth dates
BIRTH_DATE_CALENDAR_CONFIG = CalendarConfig(
    min_date=date(year=date.today().year - 200, month=1, day=1),  # 200 years ago
    max_date=date.today(),  # Today (no future dates)
)


# Dialog states for widget interactions
class BirthDataDialog(StatesGroup):
    """Dialog states for birth data collection with widgets."""

    selecting_date = State()
    selecting_time_hour = State()
    selecting_time_minute = State()


async def on_date_selected(
    callback: Any,
    widget: Any,
    manager: DialogManager,
    selected_date: date,
) -> None:
    """Handle calendar date selection.

    Implements T037: Store selected date and transition to time picker.
    Implements FR-004: Validate date immediately.
    """
    # Validate date (edge cases like dates > 200 years ago)
    await InputValidationService.validate_date(selected_date.strftime("%Y-%m-%d"))

    # Store in dialog data
    manager.dialog_data["birth_date"] = selected_date
    manager.dialog_data["validation_error"] = None

    # Move to time selection
    await manager.switch_to(BirthDataDialog.selecting_time_hour)


async def get_date_window_data(dialog_manager: DialogManager, **kwargs: Any) -> Dict[str, Any]:
    """Provide data for date selection window."""
    return {
        "prompt": "📅 Select your birth date:",
    }


async def get_time_hour_data(dialog_manager: DialogManager, **kwargs: Any) -> Dict[str, Any]:
    """Provide data for hour selection window."""
    selected_date = dialog_manager.dialog_data.get("birth_date")
    date_display = selected_date.strftime("%B %d, %Y") if selected_date else "Not selected"

    # Generate hours 0-23 for selection
    hours = [(f"{h:02d}", str(h)) for h in range(24)]

    return {
        "prompt": f"⏰ Birth date: {date_display}\n\nSelect the hour you were born:",
        "hours": hours,
    }


async def get_time_minute_data(dialog_manager: DialogManager, **kwargs: Any) -> Dict[str, Any]:
    """Provide data for minute selection window."""
    selected_hour = dialog_manager.dialog_data.get("selected_hour", 0)

    # Generate minutes in 15-minute intervals
    minutes = [(f"{selected_hour:02d}:{m:02d}", str(m)) for m in [0, 15, 30, 45]]

    return {
        "prompt": f"⏰ Hour selected: {selected_hour:02d}\n\nSelect the minute:",
        "minutes": minutes,
    }


async def on_hour_selected(
    callback: Any,
    widget: Any,
    manager: DialogManager,
    item_id: str,
) -> None:
    """Handle hour selection.

    Implements T038: Store selected hour and show minute picker.
    """
    hour = int(item_id)
    manager.dialog_data["selected_hour"] = hour

    # Move to minute selection
    await manager.switch_to(BirthDataDialog.selecting_time_minute)


async def on_minute_selected(
    callback: Any,
    widget: Any,
    manager: DialogManager,
    item_id: str,
) -> None:
    """Handle minute selection and complete dialog.

    Implements T038: Store selected time and return to main flow.
    Implements T039: Handle both natal and composite flows.
    Implements FR-005: Immediate validation.
    Implements T040: Store data in FSM context.
    """
    from ..states import ChartFlow, CompositeFlow

    minute = int(item_id)
    hour = manager.dialog_data.get("selected_hour", 0)

    # Create time object
    selected_time = time(hour=hour, minute=minute)

    # Validate time
    await InputValidationService.validate_time(f"{hour:02d}:{minute:02d}")

    # Store in dialog data
    manager.dialog_data["birth_time"] = selected_time

    # Get birth date from dialog data
    birth_date = manager.dialog_data.get("birth_date")

    # Get FSM context from event
    event = manager.event
    fsm_context = manager.middleware_data.get("state")

    if fsm_context and birth_date:
        # Get current state to determine flow type
        data = await fsm_context.get_data()
        person = data.get("dialog_for_person")  # 1 or 2 for composite, None for natal

        if person:  # Composite flow
            # Store date and time for specific person
            await fsm_context.update_data(
                **{f"birth_date_{person}": birth_date, f"birth_time_{person}": selected_time, "used_widget": True}
            )

            # Move to next state
            if person == 1:
                await fsm_context.set_state(CompositeFlow.waiting_for_location_1)
                next_prompt = "🌍 Where was the first person born?"
            else:  # person == 2
                await fsm_context.set_state(CompositeFlow.waiting_for_location_2)
                next_prompt = "🌍 Where was the second person born?"
        else:  # Natal flow
            # Store both date and time in FSM context (T040)
            await fsm_context.update_data(birth_date=birth_date, birth_time=selected_time, used_widget=True)

            # Move to location state
            await fsm_context.set_state(ChartFlow.waiting_for_location)
            next_prompt = "🌍 Finally, where were you born?"

        # Send confirmation message and prompt for location
        if event and hasattr(event, "bot") and event.bot:
            user = manager.middleware_data.get("event_from_user")
            if user and hasattr(user, "id"):
                await event.bot.send_message(
                    user.id,
                    f"✅ Date and time selected:\n"
                    f"📅 {birth_date.strftime('%B %d, %Y')}\n"
                    f"⏰ {selected_time.strftime('%H:%M')}\n\n"
                    f"{next_prompt}",
                )

    # Close dialog and return to main flow
    await manager.done()


async def on_manual_entry(
    callback: Any,
    button: Button,
    manager: DialogManager,
) -> None:
    """Handle manual entry button - exit dialog and use text input.

    Implements T038: Fallback to text input option.
    """

    # Get the birth_date from dialog_data
    birth_date = manager.dialog_data.get("birth_date")

    # Get FSM context from event
    event = manager.event
    fsm_context = manager.middleware_data.get("state")

    if fsm_context and birth_date:
        # Get current state to determine flow type
        data = await fsm_context.get_data()
        person = data.get("dialog_for_person")  # 1 or 2 for composite, None for natal

        if person:  # Composite flow
            # Store date for specific person in FSM context
            await fsm_context.update_data(**{f"birth_date_{person}": birth_date})

            # Move to time state for the appropriate person
            if person == 1:
                await fsm_context.set_state(CompositeFlow.waiting_for_time_1)
                time_prompt = (
                    "⏰ Please type the birth time for the first person\n\nExamples: '14:30', '2:30 PM', '09:15'"
                )
            else:  # person == 2
                await fsm_context.set_state(CompositeFlow.waiting_for_time_2)
                time_prompt = (
                    "⏰ Please type the birth time for the second person\n\nExamples: '14:30', '2:30 PM', '09:15'"
                )
        else:  # Natal flow
            # Store date in FSM context
            await fsm_context.update_data(birth_date=birth_date)

            # Move to time state
            await fsm_context.set_state(ChartFlow.waiting_for_time)
            time_prompt = "⏰ Please type your birth time\n\nExamples: '14:30', '2:30 PM', '09:15'"

        # Send message to user asking for manual time entry
        if event and hasattr(event, "bot") and event.bot:
            user = manager.middleware_data.get("event_from_user")
            if user and hasattr(user, "id"):
                await event.bot.send_message(
                    user.id,
                    f"✅ Date selected: {birth_date.strftime('%B %d, %Y')}\n\n{time_prompt}",
                )

    # Close dialog and return to main flow
    await manager.done()


async def on_dialog_close(result: Any, start_data: Any, manager: DialogManager) -> None:
    """Handle dialog close event - fallback to manual entry if dialog is closed without completion.

    This is called when:
    - User presses ESC or closes the dialog
    - User types a message instead of using the widget
    - Dialog is closed for any reason other than successful completion

    Args:
        result: The result returned by the dialog (if any)
        start_data: The data passed when starting the dialog
        manager: The dialog manager
    """
    # Get the birth_date from dialog data (if selected)
    birth_date = manager.dialog_data.get("birth_date")

    # Get FSM context
    fsm_context = manager.middleware_data.get("state")

    if fsm_context:
        # Get current state to determine flow type
        data = await fsm_context.get_data()
        person = data.get("dialog_for_person")  # 1 or 2 for composite, None for natal

        # Check if we have a date but no time (user was in time selection)
        if birth_date:
            # Date was selected, but time was not completed - fallback to manual time entry
            if person:  # Composite flow
                # Store date for specific person in FSM context
                await fsm_context.update_data(**{f"birth_date_{person}": birth_date})

                # Move to time state for the appropriate person
                if person == 1:
                    await fsm_context.set_state(CompositeFlow.waiting_for_time_1)
                else:  # person == 2
                    await fsm_context.set_state(CompositeFlow.waiting_for_time_2)
            else:  # Natal flow
                # Store date in FSM context
                await fsm_context.update_data(birth_date=birth_date)

                # Move to time state
                await fsm_context.set_state(ChartFlow.waiting_for_time)
        else:
            # No date was selected - fallback to manual date entry
            if person:  # Composite flow
                # Move to date state for the appropriate person
                if person == 1:
                    await fsm_context.set_state(CompositeFlow.waiting_for_date_1)
                else:  # person == 2
                    await fsm_context.set_state(CompositeFlow.waiting_for_date_2)
            else:  # Natal flow
                # Move to date state
                await fsm_context.set_state(ChartFlow.waiting_for_date)


def get_birth_data_dialog() -> Dialog:
    """Create birth data dialog with calendar and time picker.

    Returns:
        Dialog with three windows: date selection, hour selection, minute selection
    """
    return Dialog(
        # Window 1: Date selection with calendar
        Window(
            Format("{prompt}"),
            Calendar(
                id="birth_date_calendar",
                config=BIRTH_DATE_CALENDAR_CONFIG,
                on_click=on_date_selected,
            ),
            state=BirthDataDialog.selecting_date,
            getter=get_date_window_data,
        ),
        # Window 2: Hour selection (0-23)
        Window(
            Format("{prompt}"),
            Select(
                Format("{item[0]}"),
                id="hour_select",
                item_id_getter=lambda x: x[1],
                items="hours",
                on_click=on_hour_selected,
            ),
            Button(
                Const("✍️ Enter time manually"),
                id="manual_time",
                on_click=on_manual_entry,
            ),
            state=BirthDataDialog.selecting_time_hour,
            getter=get_time_hour_data,
        ),
        # Window 3: Minute selection (0, 15, 30, 45)
        Window(
            Format("{prompt}"),
            Select(
                Format("{item[0]}"),
                id="minute_select",
                item_id_getter=lambda x: x[1],
                items="minutes",
                on_click=on_minute_selected,
            ),
            Row(
                Button(
                    Const("← Back to hours"),
                    id="back_to_hours",
                    on_click=lambda c, b, m: m.switch_to(BirthDataDialog.selecting_time_hour),
                ),
                Button(
                    Const("✍️ Enter manually"),
                    id="manual_time_2",
                    on_click=on_manual_entry,
                ),
            ),
            state=BirthDataDialog.selecting_time_minute,
            getter=get_time_minute_data,
        ),
        on_process_result=on_dialog_close,
    )
