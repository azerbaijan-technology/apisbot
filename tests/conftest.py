"""Pytest configuration for tests."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, User


@pytest.fixture(scope="session", autouse=True)
def socket_allow_unix():
    """Allow unix sockets for asyncio event loops in tests."""

    import pytest_socket

    pytest_socket.socket_allow_hosts(["localhost", "127.0.0.1"])
    # Enable unix sockets for async event loops
    pytest_socket.disable_socket(allow_unix_socket=True)


@pytest.fixture
def mock_user():
    """Create a mock Telegram user."""
    return User(id=123456789, is_bot=False, first_name="TestUser")


@pytest.fixture
def mock_message(mock_user):
    """Create a mock Telegram message."""
    message = MagicMock(spec=Message)
    message.from_user = mock_user
    message.answer = AsyncMock()
    message.edit_text = AsyncMock()
    message.delete = AsyncMock()
    return message


@pytest.fixture
def mock_state():
    """Create a mock FSM state context."""
    state = MagicMock(spec=FSMContext)
    state.update_data = AsyncMock()
    state.set_state = AsyncMock()
    state.clear = AsyncMock()
    state.get_data = AsyncMock(return_value={})
    return state
