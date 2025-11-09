from aiogram.fsm.state import State, StatesGroup


class ChartSelection(StatesGroup):
    """Chart type selection state."""

    selecting_chart = State()


class ChartFlow(StatesGroup):
    """Natal chart generation flow states."""

    waiting_for_name = State()
    waiting_for_date = State()
    waiting_for_time = State()
    waiting_for_location = State()
    generating_chart = State()


class CompositeFlow(StatesGroup):
    """Composite chart generation flow states."""

    waiting_for_name_1 = State()
    waiting_for_date_1 = State()
    waiting_for_time_1 = State()
    waiting_for_location_1 = State()
    waiting_for_name_2 = State()
    waiting_for_date_2 = State()
    waiting_for_time_2 = State()
    waiting_for_location_2 = State()
    generating_composite_chart = State()
