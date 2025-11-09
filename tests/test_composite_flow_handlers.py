"""Tests for composite_flow handlers."""

from datetime import date, time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, User

from apisbot.bot.handlers.composite_flow import (
    process_date_1,
    process_date_2,
    process_location_1,
    process_location_2,
    process_name_1,
    process_name_2,
    process_time_1,
    process_time_2,
)
from apisbot.bot.states import CompositeFlow


class TestCompositeFlowPerson1:
    """Test composite flow handlers for person 1."""

    @pytest.mark.asyncio
    async def test_process_name_1(self):
        """Test name input for person 1."""
        message = MagicMock(spec=Message)
        message.text = "Person One"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()

        await process_name_1(message, state)

        state.update_data.assert_called_once()
        state.set_state.assert_called_once_with(CompositeFlow.waiting_for_date_1)

    @pytest.mark.asyncio
    async def test_process_date_1(self):
        """Test date input for person 1."""
        message = MagicMock(spec=Message)
        message.text = "1990-05-15"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()

        await process_date_1(message, state)

        state.set_state.assert_called_once_with(CompositeFlow.waiting_for_time_1)

    @pytest.mark.asyncio
    async def test_process_time_1(self):
        """Test time input for person 1."""
        message = MagicMock(spec=Message)
        message.text = "14:30"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()

        await process_time_1(message, state)

        state.set_state.assert_called_once_with(CompositeFlow.waiting_for_location_1)

    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.composite_flow.AstrologicalSubjectFactory")
    async def test_process_location_1(self, mock_subject_factory):
        """Test location input for person 1."""
        # Mock subject creation to succeed
        mock_subject = MagicMock()
        mock_subject.lat = 40.7128
        mock_subject.lng = -74.0060
        mock_subject.tz_str = "America/New_York"
        mock_subject_factory.from_birth_data.return_value = mock_subject

        message = MagicMock(spec=Message)
        message.text = "New York"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()
        state.get_data = AsyncMock(
            return_value={
                "name_1": "Person One",
                "birth_date_1": date(1990, 5, 15),
                "birth_time_1": time(14, 30),
            }
        )

        await process_location_1(message, state)

        state.update_data.assert_called()
        state.set_state.assert_called_once_with(CompositeFlow.waiting_for_name_2)


class TestCompositeFlowPerson2:
    """Test composite flow handlers for person 2."""

    @pytest.mark.asyncio
    async def test_process_name_2(self):
        """Test name input for person 2."""
        message = MagicMock(spec=Message)
        message.text = "Person Two"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()

        await process_name_2(message, state)

        state.update_data.assert_called_once()
        state.set_state.assert_called_once_with(CompositeFlow.waiting_for_date_2)

    @pytest.mark.asyncio
    async def test_process_date_2(self):
        """Test date input for person 2."""
        message = MagicMock(spec=Message)
        message.text = "1985-12-25"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()

        await process_date_2(message, state)

        state.set_state.assert_called_once_with(CompositeFlow.waiting_for_time_2)

    @pytest.mark.asyncio
    async def test_process_time_2(self):
        """Test time input for person 2."""
        message = MagicMock(spec=Message)
        message.text = "08:00"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()

        await process_time_2(message, state)

        state.set_state.assert_called_once_with(CompositeFlow.waiting_for_location_2)

    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.composite_flow.AstrologicalSubjectFactory")
    @patch("apisbot.bot.handlers.composite_flow.ChartService")
    @patch("apisbot.bot.handlers.composite_flow.ConverterService")
    async def test_process_location_2_success(self, mock_converter_class, mock_chart_class, mock_subject_factory):
        """Test successful composite chart generation."""
        # Mock subject creation to succeed
        mock_subject_2 = MagicMock()
        mock_subject_2.name = "Person Two"
        mock_subject_2.lat = 51.5074
        mock_subject_2.lng = -0.1278
        mock_subject_2.tz_str = "Europe/London"
        mock_subject_factory.from_birth_data.return_value = mock_subject_2

        # Setup mocks
        mock_chart_service = MagicMock()
        mock_chart_service.generate_composite = AsyncMock(return_value="<svg>composite chart</svg>")
        mock_chart_class.return_value = mock_chart_service

        mock_converter_service = MagicMock()
        mock_converter_service.svg_to_png = AsyncMock(return_value=b"PNG_DATA")
        mock_converter_class.return_value = mock_converter_service

        message = MagicMock(spec=Message)
        message.text = "London, UK"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock(return_value=MagicMock(delete=AsyncMock()))
        message.answer_photo = AsyncMock()

        # Create mock subject_1 (from first person's data)
        mock_subject_1 = MagicMock()
        mock_subject_1.name = "Person One"
        mock_subject_1.lat = 40.7128
        mock_subject_1.lng = -74.0060
        mock_subject_1.tz_str = "America/New_York"

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()
        state.get_data = AsyncMock(
            return_value={
                "name_1": "Person One",
                "birth_date_1": date(1990, 5, 15),
                "birth_time_1": time(14, 30),
                "location_1": "New York",
                "subject_1": mock_subject_1,
                "name_2": "Person Two",
                "birth_date_2": date(1985, 12, 25),
                "birth_time_2": time(8, 0),
            }
        )
        state.clear = AsyncMock()

        await process_location_2(message, state)

        # Verify composite chart was generated
        mock_chart_service.generate_composite.assert_called_once()
        message.answer_photo.assert_called_once()
        state.clear.assert_called_once()
