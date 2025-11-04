"""Tests for chart_flow handlers."""

from datetime import date, time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, User

from apisbot.bot.handlers.chart_flow import process_date, process_location, process_name, process_time
from apisbot.bot.states import ChartFlow


class TestProcessName:
    """Test process_name handler."""

    @pytest.mark.asyncio
    async def test_process_name_valid(self):
        """Test valid name input."""
        message = MagicMock(spec=Message)
        message.text = "John Doe"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()

        await process_name(message, state)

        state.update_data.assert_called_once_with(name="John Doe")
        state.set_state.assert_called_once_with(ChartFlow.waiting_for_date)
        message.answer.assert_called_once()

        # Check message contains date format info
        call_args = message.answer.call_args[0][0]
        assert "date" in call_args.lower()

    @pytest.mark.asyncio
    async def test_process_name_with_whitespace(self):
        """Test name with extra whitespace."""
        message = MagicMock(spec=Message)
        message.text = "  Jane Smith  "
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()

        await process_name(message, state)

        state.update_data.assert_called_once_with(name="Jane Smith")

    @pytest.mark.asyncio
    async def test_process_name_empty(self):
        """Test empty name."""
        message = MagicMock(spec=Message)
        message.text = "   "  # Whitespace only
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()

        await process_name(message, state)

        state.update_data.assert_not_called()
        state.set_state.assert_not_called()
        message.answer.assert_called_once()
        assert "must be between 1 and 100" in message.answer.call_args[0][0]

    @pytest.mark.asyncio
    async def test_process_name_too_long(self):
        """Test name that's too long."""
        message = MagicMock(spec=Message)
        message.text = "a" * 101
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()

        await process_name(message, state)

        state.update_data.assert_not_called()
        message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_name_no_letters(self):
        """Test name with no letters."""
        message = MagicMock(spec=Message)
        message.text = "123456"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()

        await process_name(message, state)

        state.update_data.assert_not_called()
        message.answer.assert_called_once()
        assert "letter" in message.answer.call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_process_name_no_text(self):
        """Test message with no text."""
        message = MagicMock(spec=Message)
        message.text = None
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)

        await process_name(message, state)

        message.answer.assert_called_once()
        assert "text message" in message.answer.call_args[0][0].lower()


class TestProcessDate:
    """Test process_date handler."""

    @pytest.mark.asyncio
    async def test_process_date_valid(self):
        """Test valid date input."""
        message = MagicMock(spec=Message)
        message.text = "1990-05-15"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()

        await process_date(message, state)

        # Check that birth_date was stored
        call_args = state.update_data.call_args[1]
        assert "birth_date" in call_args
        assert call_args["birth_date"] == date(1990, 5, 15)

        state.set_state.assert_called_once_with(ChartFlow.waiting_for_time)
        message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_date_invalid_format(self):
        """Test invalid date format."""
        message = MagicMock(spec=Message)
        message.text = "invalid date"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()

        await process_date(message, state)

        state.update_data.assert_not_called()
        state.set_state.assert_not_called()
        message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_date_no_text(self):
        """Test message with no text."""
        message = MagicMock(spec=Message)
        message.text = None
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)

        await process_date(message, state)

        message.answer.assert_called_once()
        assert "text message" in message.answer.call_args[0][0].lower()


class TestProcessTime:
    """Test process_time handler."""

    @pytest.mark.asyncio
    async def test_process_time_valid(self):
        """Test valid time input."""
        message = MagicMock(spec=Message)
        message.text = "14:30"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()

        await process_time(message, state)

        # Check that birth_time was stored
        call_args = state.update_data.call_args[1]
        assert "birth_time" in call_args
        assert call_args["birth_time"] == time(14, 30)

        state.set_state.assert_called_once_with(ChartFlow.waiting_for_location)
        message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_time_invalid_format(self):
        """Test invalid time format."""
        message = MagicMock(spec=Message)
        message.text = "invalid time"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()

        await process_time(message, state)

        state.update_data.assert_not_called()
        state.set_state.assert_not_called()
        message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_time_no_text(self):
        """Test message with no text."""
        message = MagicMock(spec=Message)
        message.text = None
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)

        await process_time(message, state)

        message.answer.assert_called_once()
        assert "text message" in message.answer.call_args[0][0].lower()


class TestProcessLocation:
    """Test process_location handler."""

    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.chart_flow.ChartService")
    @patch("apisbot.bot.handlers.chart_flow.ConverterService")
    async def test_process_location_success(self, mock_converter_class, mock_chart_class):
        """Test successful location processing and chart generation."""
        # Setup mocks
        mock_chart_service = MagicMock()
        mock_chart_service.generate_chart = AsyncMock(return_value="<svg>chart</svg>")
        mock_chart_class.return_value = mock_chart_service

        mock_converter_service = MagicMock()
        mock_converter_service.svg_to_png = AsyncMock(return_value=b"PNG_DATA")
        mock_converter_class.return_value = mock_converter_service

        message = MagicMock(spec=Message)
        message.text = "New York, USA"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock(return_value=MagicMock(delete=AsyncMock()))
        message.answer_photo = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()
        state.get_data = AsyncMock(
            return_value={
                "name": "John Doe",
                "birth_date": date(1990, 5, 15),
                "birth_time": time(14, 30),
            }
        )
        state.clear = AsyncMock()

        await process_location(message, state)

        # Verify chart was generated and sent
        mock_chart_service.generate_chart.assert_called_once()
        mock_converter_service.svg_to_png.assert_called_once()
        message.answer_photo.assert_called_once()
        state.clear.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_location_too_short(self):
        """Test location that's too short."""
        message = MagicMock(spec=Message)
        message.text = "A"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()

        await process_location(message, state)

        state.update_data.assert_not_called()
        message.answer.assert_called_once()
        assert "between 2 and 200" in message.answer.call_args[0][0]

    @pytest.mark.asyncio
    async def test_process_location_too_long(self):
        """Test location that's too long."""
        message = MagicMock(spec=Message)
        message.text = "A" * 201
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)

        await process_location(message, state)

        message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_location_no_text(self):
        """Test message with no text."""
        message = MagicMock(spec=Message)
        message.text = None
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)

        await process_location(message, state)

        message.answer.assert_called_once()
        assert "text message" in message.answer.call_args[0][0].lower()

    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.chart_flow.ChartService")
    async def test_process_location_geocoding_error(self, mock_chart_class):
        """Test location geocoding error."""
        mock_chart_service = MagicMock()
        mock_chart_service.generate_chart = AsyncMock(side_effect=ValueError("Could not find location"))
        mock_chart_class.return_value = mock_chart_service

        message = MagicMock(spec=Message)
        message.text = "InvalidLocation123"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock(return_value=MagicMock(delete=AsyncMock()))

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()
        state.get_data = AsyncMock(
            return_value={
                "name": "John Doe",
                "birth_date": date(1990, 5, 15),
                "birth_time": time(14, 30),
            }
        )

        await process_location(message, state)

        # Should return to location state
        state.set_state.assert_called_with(ChartFlow.waiting_for_location)

    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.chart_flow.ChartService")
    async def test_process_location_generic_error(self, mock_chart_class):
        """Test generic error during chart generation."""
        mock_chart_service = MagicMock()
        mock_chart_service.generate_chart = AsyncMock(side_effect=ValueError("Some other error"))
        mock_chart_class.return_value = mock_chart_service

        message = MagicMock(spec=Message)
        message.text = "New York"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock(return_value=MagicMock(delete=AsyncMock()))

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()
        state.get_data = AsyncMock(
            return_value={
                "name": "John Doe",
                "birth_date": date(1990, 5, 15),
                "birth_time": time(14, 30),
            }
        )
        state.clear = AsyncMock()

        await process_location(message, state)

        # Should clear state
        state.clear.assert_called_once()

    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.chart_flow.ChartService")
    async def test_process_location_unexpected_error(self, mock_chart_class):
        """Test unexpected error during chart generation."""
        mock_chart_service = MagicMock()
        mock_chart_service.generate_chart = AsyncMock(side_effect=Exception("Unexpected error"))
        mock_chart_class.return_value = mock_chart_service

        message = MagicMock(spec=Message)
        message.text = "New York"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock(return_value=MagicMock(delete=AsyncMock()))

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()
        state.get_data = AsyncMock(
            return_value={
                "name": "John Doe",
                "birth_date": date(1990, 5, 15),
                "birth_time": time(14, 30),
            }
        )
        state.clear = AsyncMock()

        await process_location(message, state)

        # Should clear state
        state.clear.assert_called_once()
