"""Tests for bot states."""

from aiogram.fsm.state import State

from apisbot.bot.states import ChartFlow, CompositeFlow


class TestChartFlow:
    """Test ChartFlow state definitions."""

    def test_chart_flow_states_exist(self):
        """Test that all ChartFlow states are defined."""
        assert hasattr(ChartFlow, "waiting_for_name")
        assert hasattr(ChartFlow, "waiting_for_date")
        assert hasattr(ChartFlow, "waiting_for_time")
        assert hasattr(ChartFlow, "waiting_for_location")
        assert hasattr(ChartFlow, "generating_chart")

    def test_chart_flow_states_are_state_objects(self):
        """Test that ChartFlow states are State instances."""
        assert isinstance(ChartFlow.waiting_for_name, State)
        assert isinstance(ChartFlow.waiting_for_date, State)
        assert isinstance(ChartFlow.waiting_for_time, State)
        assert isinstance(ChartFlow.waiting_for_location, State)
        assert isinstance(ChartFlow.generating_chart, State)

    def test_chart_flow_states_unique(self):
        """Test that ChartFlow states are unique."""
        states = [
            ChartFlow.waiting_for_name,
            ChartFlow.waiting_for_date,
            ChartFlow.waiting_for_time,
            ChartFlow.waiting_for_location,
            ChartFlow.generating_chart,
        ]

        # Check that all state names are unique
        state_names = [state.state for state in states]
        assert len(state_names) == len(set(state_names))


class TestCompositeFlow:
    """Test CompositeFlow state definitions."""

    def test_composite_flow_states_exist(self):
        """Test that all CompositeFlow states are defined."""
        assert hasattr(CompositeFlow, "waiting_for_name_1")
        assert hasattr(CompositeFlow, "waiting_for_date_1")
        assert hasattr(CompositeFlow, "waiting_for_time_1")
        assert hasattr(CompositeFlow, "waiting_for_location_1")
        assert hasattr(CompositeFlow, "waiting_for_name_2")
        assert hasattr(CompositeFlow, "waiting_for_date_2")
        assert hasattr(CompositeFlow, "waiting_for_time_2")
        assert hasattr(CompositeFlow, "waiting_for_location_2")
        assert hasattr(CompositeFlow, "generating_composite_chart")

    def test_composite_flow_states_are_state_objects(self):
        """Test that CompositeFlow states are State instances."""
        assert isinstance(CompositeFlow.waiting_for_name_1, State)
        assert isinstance(CompositeFlow.waiting_for_date_1, State)
        assert isinstance(CompositeFlow.waiting_for_time_1, State)
        assert isinstance(CompositeFlow.waiting_for_location_1, State)
        assert isinstance(CompositeFlow.waiting_for_name_2, State)
        assert isinstance(CompositeFlow.waiting_for_date_2, State)
        assert isinstance(CompositeFlow.waiting_for_time_2, State)
        assert isinstance(CompositeFlow.waiting_for_location_2, State)
        assert isinstance(CompositeFlow.generating_composite_chart, State)

    def test_composite_flow_states_unique(self):
        """Test that CompositeFlow states are unique."""
        states = [
            CompositeFlow.waiting_for_name_1,
            CompositeFlow.waiting_for_date_1,
            CompositeFlow.waiting_for_time_1,
            CompositeFlow.waiting_for_location_1,
            CompositeFlow.waiting_for_name_2,
            CompositeFlow.waiting_for_date_2,
            CompositeFlow.waiting_for_time_2,
            CompositeFlow.waiting_for_location_2,
            CompositeFlow.generating_composite_chart,
        ]

        # Check that all state names are unique
        state_names = [state.state for state in states]
        assert len(state_names) == len(set(state_names))
