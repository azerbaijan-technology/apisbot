from aiogram.fsm.state import State, StatesGroup


class ChartFlow(StatesGroup):
    """Conversation flow states for natal chart generation.

    States represent the progression of collecting birth information:
    1. waiting_for_name: User provides their name
    2. waiting_for_date: User provides birth date
    3. waiting_for_time: User provides birth time
    4. waiting_for_location: User provides birth location
    5. generating_chart: Transient state while processing chart
    """

    waiting_for_name = State()
    waiting_for_date = State()
    waiting_for_time = State()
    waiting_for_location = State()
    generating_chart = State()


class CompositeFlow(StatesGroup):
    waiting_for_name_1 = State()
    waiting_for_date_1 = State()
    waiting_for_time_1 = State()
    waiting_for_location_1 = State()
    waiting_for_name_2 = State()
    waiting_for_date_2 = State()
    waiting_for_time_2 = State()
    waiting_for_location_2 = State()
    generating_composite_chart = State()
