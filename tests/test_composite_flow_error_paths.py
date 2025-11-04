"""Tests for composite_flow error paths to increase coverage."""

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


class TestCompositeFlowErrorPaths:
    """Test error handling in composite flow."""

    @pytest.mark.asyncio
    async def test_process_name_1_invalid(self):
        """Test invalid name for person 1."""
        message = MagicMock(spec=Message)
        message.text = "123"  # No letters
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()

        await process_name_1(message, state)

        state.update_data.assert_not_called()
        message.answer.assert_called()

    @pytest.mark.asyncio
    async def test_process_name_2_invalid(self):
        """Test invalid name for person 2."""
        message = MagicMock(spec=Message)
        message.text = ""
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)

        await process_name_2(message, state)

        message.answer.assert_called()

    @pytest.mark.asyncio
    async def test_process_date_1_invalid(self):
        """Test invalid date for person 1."""
        message = MagicMock(spec=Message)
        message.text = "invalid"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.set_state = AsyncMock()

        await process_date_1(message, state)

        state.set_state.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_date_2_invalid(self):
        """Test invalid date for person 2."""
        message = MagicMock(spec=Message)
        message.text = "not a date"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)

        await process_date_2(message, state)

        message.answer.assert_called()

    @pytest.mark.asyncio
    async def test_process_time_1_invalid(self):
        """Test invalid time for person 1."""
        message = MagicMock(spec=Message)
        message.text = "invalid"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.set_state = AsyncMock()

        await process_time_1(message, state)

        state.set_state.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_time_2_invalid(self):
        """Test invalid time for person 2."""
        message = MagicMock(spec=Message)
        message.text = "not a time"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)

        await process_time_2(message, state)

        message.answer.assert_called()

    @pytest.mark.asyncio
    async def test_process_location_1_invalid(self):
        """Test invalid location for person 1."""
        message = MagicMock(spec=Message)
        message.text = "A"  # Too short
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()

        await process_location_1(message, state)

        state.update_data.assert_not_called()

    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.composite_flow.ChartService")
    async def test_process_location_2_chart_error(self, mock_chart_class):
        """Test chart generation error for composite."""
        mock_chart_service = MagicMock()
        mock_chart_service.generate_composite = AsyncMock(
            side_effect=ValueError("Could not find location for first person")
        )
        mock_chart_class.return_value = mock_chart_service

        message = MagicMock(spec=Message)
        message.text = "London"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock(return_value=MagicMock(delete=AsyncMock()))

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()
        state.get_data = AsyncMock(
            return_value={
                "name_1": "Person One",
                "birth_date_1": date(1990, 5, 15),
                "birth_time_1": time(14, 30),
                "location_1": "InvalidLocation",
                "name_2": "Person Two",
                "birth_date_2": date(1985, 12, 25),
                "birth_time_2": time(8, 0),
                "location_2": "London",
            }
        )

        await process_location_2(message, state)

        # Should handle error gracefully
        message.answer.assert_called()

    @pytest.mark.asyncio
    async def test_process_name_1_no_text(self):
        """Test no text message for person 1."""
        message = MagicMock(spec=Message)
        message.text = None
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)

        await process_name_1(message, state)

        message.answer.assert_called()

    @pytest.mark.asyncio
    async def test_process_date_1_no_text(self):
        """Test no text message for date 1."""
        message = MagicMock(spec=Message)
        message.text = None
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)

        await process_date_1(message, state)

        message.answer.assert_called()

    @pytest.mark.asyncio
    async def test_process_time_1_no_text(self):
        """Test no text message for time 1."""
        message = MagicMock(spec=Message)
        message.text = None
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)

        await process_time_1(message, state)

        message.answer.assert_called()

    @pytest.mark.asyncio
    async def test_process_location_1_no_text(self):
        """Test no text message for location 1."""
        message = MagicMock(spec=Message)
        message.text = None
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)

        await process_location_1(message, state)

        message.answer.assert_called()

    @pytest.mark.asyncio
    async def test_process_name_2_no_text(self):
        """Test no text message for person 2."""
        message = MagicMock(spec=Message)
        message.text = None
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)

        await process_name_2(message, state)

        message.answer.assert_called()

    @pytest.mark.asyncio
    async def test_process_date_2_no_text(self):
        """Test no text message for date 2."""
        message = MagicMock(spec=Message)
        message.text = None
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)

        await process_date_2(message, state)

        message.answer.assert_called()

    @pytest.mark.asyncio
    async def test_process_time_2_no_text(self):
        """Test no text message for time 2."""
        message = MagicMock(spec=Message)
        message.text = None
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)

        await process_time_2(message, state)

        message.answer.assert_called()

    @pytest.mark.asyncio
    async def test_process_location_2_no_text(self):
        """Test no text message for location 2."""
        message = MagicMock(spec=Message)
        message.text = None
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)

        await process_location_2(message, state)

        message.answer.assert_called()

    @pytest.mark.asyncio
    async def test_process_location_2_too_short(self):
        """Test location 2 that's too short."""
        message = MagicMock(spec=Message)
        message.text = "X"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)

        await process_location_2(message, state)

        message.answer.assert_called()

    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.composite_flow.ChartService")
    async def test_process_location_2_generic_error(self, mock_chart_class):
        """Test generic error during composite chart generation."""
        mock_chart_service = MagicMock()
        mock_chart_service.generate_composite = AsyncMock(side_effect=ValueError("Some other error"))
        mock_chart_class.return_value = mock_chart_service

        message = MagicMock(spec=Message)
        message.text = "London"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock(return_value=MagicMock(delete=AsyncMock()))

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()
        state.get_data = AsyncMock(
            return_value={
                "name_1": "Person One",
                "birth_date_1": date(1990, 5, 15),
                "birth_time_1": time(14, 30),
                "location_1": "New York",
                "name_2": "Person Two",
                "birth_date_2": date(1985, 12, 25),
                "birth_time_2": time(8, 0),
                "location_2": "London",
            }
        )
        state.clear = AsyncMock()

        await process_location_2(message, state)

        # Should clear state on generic error
        state.clear.assert_called()

    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.composite_flow.ChartService")
    async def test_process_location_2_unexpected_error(self, mock_chart_class):
        """Test unexpected exception during composite chart generation."""
        mock_chart_service = MagicMock()
        mock_chart_service.generate_composite = AsyncMock(side_effect=Exception("Unexpected error"))
        mock_chart_class.return_value = mock_chart_service

        message = MagicMock(spec=Message)
        message.text = "London"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock(return_value=MagicMock(delete=AsyncMock()))

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()
        state.get_data = AsyncMock(
            return_value={
                "name_1": "Person One",
                "birth_date_1": date(1990, 5, 15),
                "birth_time_1": time(14, 30),
                "location_1": "New York",
                "name_2": "Person Two",
                "birth_date_2": date(1985, 12, 25),
                "birth_time_2": time(8, 0),
                "location_2": "London",
            }
        )
        state.clear = AsyncMock()

        await process_location_2(message, state)

        # Should clear state on unexpected error
        state.clear.assert_called()
