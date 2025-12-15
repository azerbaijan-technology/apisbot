"""Tests for transit_flow handlers."""

from datetime import date, time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, User

from apisbot.bot.handlers.transit_flow import (
    process_date_1,
    process_date_2,
    process_location_1,
    process_location_2,
    process_name_1,
    process_name_2,
    process_time_1,
    process_time_2,
)
from apisbot.bot.states import TransitFlow


class TestTransitFlow:
    """Test transit flow handlers."""

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
        state.set_state.assert_called_once_with(TransitFlow.waiting_for_date_1)

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

        state.set_state.assert_called_once_with(TransitFlow.waiting_for_time_1)

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

        state.set_state.assert_called_once_with(TransitFlow.waiting_for_location_1)

    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.transit_flow.AstrologicalSubjectFactory")
    async def test_process_location_1(self, mock_subject_factory):
        """Test location input for person 1."""
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

        # Mock successful subject creation
        mock_subject_factory.from_birth_data.return_value = MagicMock()

        await process_location_1(message, state)

        state.update_data.assert_called()
        state.set_state.assert_called_once_with(TransitFlow.waiting_for_name_2)

    @pytest.mark.asyncio
    async def test_process_name_2(self):
        """Test name input for transit subject."""
        message = MagicMock(spec=Message)
        message.text = "Transit Name"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()

        await process_name_2(message, state)

        state.update_data.assert_called_once()
        state.set_state.assert_called_once_with(TransitFlow.waiting_for_date_2)

    @pytest.mark.asyncio
    async def test_process_date_2(self):
        """Test date input for transit."""
        message = MagicMock(spec=Message)
        message.text = "2024-01-01"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()

        await process_date_2(message, state)

        state.set_state.assert_called_once_with(TransitFlow.waiting_for_time_2)

    @pytest.mark.asyncio
    async def test_process_time_2(self):
        """Test time input for transit."""
        message = MagicMock(spec=Message)
        message.text = "12:00"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()

        await process_time_2(message, state)

        state.set_state.assert_called_once_with(TransitFlow.waiting_for_location_2)

    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.transit_flow.ChartService")
    @patch("apisbot.bot.handlers.transit_flow.ConverterService")
    @patch("apisbot.bot.handlers.transit_flow.AstrologicalSubjectFactory")
    async def test_process_location_2_success(self, mock_subject_factory, mock_converter_class, mock_chart_class):
        """Test successful transit chart generation."""
        # Setup mocks
        mock_chart_service = MagicMock()
        mock_chart_service.generate_transit = AsyncMock(return_value="<svg>transit chart</svg>")
        mock_chart_class.return_value = mock_chart_service

        mock_converter_service = MagicMock()
        mock_converter_service.svg_to_png = AsyncMock(return_value=b"PNG_DATA")
        mock_converter_class.return_value = mock_converter_service

        message = MagicMock(spec=Message)
        message.text = "London, UK"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock(return_value=MagicMock(delete=AsyncMock()))
        message.answer_photo = AsyncMock()

        state = MagicMock(spec=FSMContext)
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()
        state.get_data = AsyncMock(
            return_value={
                "name_1": "Person One",
                "birth_date_1": date(1990, 5, 15),
                "birth_time_1": time(14, 30),
                "location_1": "New York",
                "subject_1": MagicMock(),  # subject_1 is stored from step 1
                "name_2": "Transit",
                "birth_date_2": date(2024, 1, 1),
                "birth_time_2": time(12, 0),
                "location_2": "London, UK",
            }
        )
        state.clear = AsyncMock()

        # Mock subject creation for transit
        mock_subject_factory.from_birth_data.return_value = MagicMock()

        await process_location_2(message, state)

        # Verify transit chart was generated
        mock_chart_service.generate_transit.assert_called_once()
        message.answer_photo.assert_called_once()
        state.clear.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_name_1_validations(self):
        """Test name validation for person 1."""
        state = MagicMock(spec=FSMContext)
        message = MagicMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        # Test empty text
        message.text = None
        await process_name_1(message, state)
        message.answer.assert_called_with("❌ Please provide a text message with the name.")

        # Test length > 100
        message.text = "a" * 101
        await process_name_1(message, state)
        assert "Name must be between 1 and 100" in message.answer.call_args[0][0]

        # Test no letters
        message.text = "12345"
        await process_name_1(message, state)
        assert "Name must contain at least one letter" in message.answer.call_args[0][0]

    @pytest.mark.asyncio
    async def test_process_date_1_validations(self):
        """Test date validation for person 1."""
        state = MagicMock(spec=FSMContext)
        message = MagicMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        # Empty
        message.text = None
        await process_date_1(message, state)
        assert "Please provide a text message" in message.answer.call_args[0][0]

        # Invalid format
        message.text = "invalid-date"
        await process_date_1(message, state)
        assert "❌" in message.answer.call_args[0][0]

    @pytest.mark.asyncio
    async def test_process_time_1_validations(self):
        """Test time validation for person 1."""
        state = MagicMock(spec=FSMContext)
        message = MagicMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        # Empty
        message.text = None
        await process_time_1(message, state)
        assert "Please provide a text message" in message.answer.call_args[0][0]

        # Invalid format
        message.text = "invalid-time"
        await process_time_1(message, state)
        assert "❌" in message.answer.call_args[0][0]

    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.transit_flow.AstrologicalSubjectFactory")
    async def test_process_location_1_validations(self, mock_subject_factory):
        """Test location validation for person 1."""
        state = MagicMock(spec=FSMContext)
        state.get_data = AsyncMock(return_value={"name_1": "Test", "birth_date_1": date(2000,1,1), "birth_time_1": time(12,0)})
        state.set_state = AsyncMock()
        
        message = MagicMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        # Empty
        message.text = None
        await process_location_1(message, state)
        assert "Please provide a text message" in message.answer.call_args[0][0]

        # Short
        message.text = "a"
        await process_location_1(message, state)
        assert "Location must be between" in message.answer.call_args[0][0]
        
        # Trigger "Location Error" branch logic
        # Code checks for "location", "city", or "geonames"
        # Then checks for "first" or "second" to decide which subject
        # If "first" is not in msg, it defaults to "second"? 
        # Let's inspect the code logic for process_location_1 again. 
        # If it uses the SAME helper or copy-pasted logic, we need to be careful.
        # Use "city not found for first person" to be safe.
        mock_subject_factory.from_birth_data.side_effect = ValueError("city not found for first person")
        message.text = "New York"
        
        await process_location_1(message, state)
        # Should hit the Location Error branch
        assert "Location Error" in message.answer.call_args[0][0]

    @pytest.mark.asyncio
    async def test_process_location_1_unexpected_error(self):
        """Test unexpected error in location 1."""
        state = MagicMock(spec=FSMContext)
        message = MagicMock(spec=Message)
        message.text = "Kyiv"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()
        
        with patch("apisbot.bot.handlers.transit_flow.AstrologicalSubjectFactory") as mock_factory:
            mock_factory.from_birth_data.side_effect = RuntimeError("Boom")
            
            await process_location_1(message, state)
            
            assert "Unexpected Error" in message.answer.call_args[0][0]
            state.clear.assert_not_called() # Should it clear? Usually unexpected errors in flow might not clear if recoverable? 
            # In transit_flow line 172 (from cached view), it returns.
            # Lines 166-172 handle unexpected exceptions.
            # It just asks to try again. It does NOT call state.clear() in that block in the snippet I saw (line 174 is success path).
            
    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.transit_flow.ChartService")
    @patch("apisbot.bot.handlers.transit_flow.AstrologicalSubjectFactory")
    async def test_process_location_2_unexpected_error(self, mock_subject_factory, mock_chart_class):
        """Test unexpected error during transit chart generation."""
        state = MagicMock(spec=FSMContext)
        state.get_data = AsyncMock(return_value={
            "name_1": "Test", "birth_date_1": date(2000,1,1), "birth_time_1": time(12,0),
            "location_1": "Loc1", "subject_1": MagicMock(),
            "name_2": "Transit", "birth_date_2": date(2024,1,1), "birth_time_2": time(12,0)
        })
        state.set_state = AsyncMock()
        
        message = MagicMock(spec=Message)
        message.text = "Loc2"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock(return_value=MagicMock(delete=AsyncMock()))
        
        # Mock unexpected failure
        mock_subject_factory.from_birth_data.return_value = MagicMock()
        mock_chart_class.generate_transit.side_effect = RuntimeError("Unexpected crash")
        
        await process_location_2(message, state)
        
        assert "Unexpected Error" in message.answer.call_args_list[-1][0][0]

    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.transit_flow.ChartService")
    @patch("apisbot.bot.handlers.transit_flow.AstrologicalSubjectFactory")
    async def test_process_location_2_error(self, mock_subject_factory, mock_chart_class):
        """Test error during transit chart generation."""
        state = MagicMock(spec=FSMContext)
        state.get_data = AsyncMock(return_value={
            "name_1": "Test", "birth_date_1": date(2000,1,1), "birth_time_1": time(12,0),
            "location_1": "Loc1", "subject_1": MagicMock(),
            "name_2": "Transit", "birth_date_2": date(2024,1,1), "birth_time_2": time(12,0)
        })
        state.set_state = AsyncMock()
        
        message = MagicMock(spec=Message)
        message.text = "Loc2"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock(return_value=MagicMock(delete=AsyncMock()))
        
        # Mock failure
        mock_subject_factory.from_birth_data.return_value = MagicMock()
        mock_chart_service = MagicMock()
        mock_chart_service.generate_transit = AsyncMock(side_effect=ValueError("Generation failed"))
        mock_chart_class.return_value = mock_chart_service
        
        await process_location_2(message, state)
        
        assert "Generation failed" in message.answer.call_args_list[-1][0][0]

    @pytest.mark.asyncio
    async def test_process_name_2_validations(self):
        """Test name validation for transit."""
        state = MagicMock(spec=FSMContext)
        message = MagicMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        message.text = None
        await process_name_2(message, state)
        assert "Please provide a text message" in message.answer.call_args[0][0]

    @pytest.mark.asyncio
    async def test_process_date_2_validations(self):
        state = MagicMock(spec=FSMContext)
        message = MagicMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        message.text = "invalid"
        await process_date_2(message, state)
        assert "❌" in message.answer.call_args[0][0]

    @pytest.mark.asyncio
    async def test_process_time_2_validations(self):
        state = MagicMock(spec=FSMContext)
        message = MagicMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        message.text = "invalid"
        await process_time_2(message, state)
        assert "❌" in message.answer.call_args[0][0]

    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.transit_flow.ChartService")
    @patch("apisbot.bot.handlers.transit_flow.AstrologicalSubjectFactory")
    async def test_process_location_2_geonames_error(self, mock_subject_factory, mock_chart_class):
        """Test location 2 geocoding error (triggers tips)."""
        state = MagicMock(spec=FSMContext)
        state.get_data = AsyncMock(return_value={
            "name_1": "Test", "birth_date_1": date(2000,1,1), "birth_time_1": time(12,0),
            "location_1": "Loc1", "subject_1": MagicMock(),
            "name_2": "Transit", "birth_date_2": date(2024,1,1), "birth_time_2": time(12,0)
        })
        state.set_state = AsyncMock()
        
        message = MagicMock(spec=Message)
        message.text = "Nowhere"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock(return_value=MagicMock(delete=AsyncMock()))
        
        mock_subject_factory.from_birth_data.side_effect = ValueError("city not found")
        
        await process_location_2(message, state)
        
        # Should trigger tips
        assert "Location Error" in message.answer.call_args[0][0]

    @pytest.mark.asyncio
    @patch("apisbot.bot.handlers.transit_flow.AstrologicalSubjectFactory")
    async def test_process_location_1_generic_error(self, mock_subject_factory):
        """Test generic error in location 1 (not city not found)."""
        state = MagicMock(spec=FSMContext)
        state.get_data = AsyncMock(return_value={"name_1": "Test", "birth_date_1": date(2000,1,1), "birth_time_1": time(12,0)})
        
        message = MagicMock(spec=Message)
        message.text = "Nowhere"
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()
        
        mock_subject_factory.from_birth_data.side_effect = ValueError("Some other error")
        
        await process_location_1(message, state)
        
        assert "Transit Chart Generation Failed" in message.answer.call_args[0][0]

    @pytest.mark.asyncio
    async def test_process_name_2_extra_validations(self):
        """Test name 2 extra validation paths."""
        state = MagicMock(spec=FSMContext)
        message = MagicMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()

        # Too long
        message.text = "a" * 101
        await process_name_2(message, state)
        assert "Name must be between" in message.answer.call_args[0][0]

        # No alpha
        message.text = "123"
        await process_name_2(message, state)
        assert "Name must contain at least one letter" in message.answer.call_args[0][0]

