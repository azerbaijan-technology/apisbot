"""Pytest configuration for tests."""

import pytest


@pytest.fixture(scope="session", autouse=True)
def socket_allow_unix():
    """Allow unix sockets for asyncio event loops in tests."""

    import pytest_socket

    pytest_socket.socket_allow_hosts(["localhost", "127.0.0.1"])
    # Enable unix sockets for async event loops
    pytest_socket.disable_socket(allow_unix_socket=True)
