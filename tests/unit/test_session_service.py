"""Unit tests for session service.

Tests session lifecycle, timeout management, and privacy-first cleanup.
Framework-agnostic: No aiogram dependencies required.
"""

import asyncio
from datetime import datetime

import pytest

from src.apisbot.models.chart_selection import ChartSelection
from src.apisbot.services.session_service import SessionService, get_session_service


class TestSessionServiceLifecycle:
    """Test suite for session creation and retrieval."""

    @pytest.mark.asyncio
    async def test_get_or_create_session_creates_new_session(self):
        """Test that get_or_create_session creates new session for new user."""
        service = SessionService()
        user_id = 12345

        session = await service.get_or_create_session(user_id)

        assert session.user_id == user_id
        assert session.chart_type is None
        assert session.person1_data is None
        assert session.person2_data is None
        assert session.timeout_seconds == 1800  # Default 30 minutes

    @pytest.mark.asyncio
    async def test_get_or_create_session_returns_existing_session(self):
        """Test that get_or_create_session returns existing session for known user."""
        service = SessionService()
        user_id = 12345

        # Create initial session
        session1 = await service.get_or_create_session(user_id)
        session1.chart_type = ChartSelection.NATAL

        # Retrieve same session
        session2 = await service.get_or_create_session(user_id)

        assert session2.user_id == user_id
        assert session2.chart_type == ChartSelection.NATAL
        # Should be the same session object
        assert session1 is session2

    @pytest.mark.asyncio
    async def test_get_or_create_session_updates_activity_timestamp(self):
        """Test that retrieving session updates last_updated timestamp."""
        service = SessionService()
        user_id = 12345

        # Create session
        session1 = await service.get_or_create_session(user_id)
        first_timestamp = session1.last_updated

        # Wait a bit
        await asyncio.sleep(0.1)

        # Retrieve session again
        session2 = await service.get_or_create_session(user_id)
        second_timestamp = session2.last_updated

        # Timestamp should have been updated
        assert second_timestamp > first_timestamp

    @pytest.mark.asyncio
    async def test_get_or_create_session_multiple_users_independent(self):
        """Test that sessions for different users are independent."""
        service = SessionService()
        user_id_1 = 12345
        user_id_2 = 67890

        # Create sessions for two users
        session1 = await service.get_or_create_session(user_id_1)
        session2 = await service.get_or_create_session(user_id_2)

        # Modify first session
        session1.chart_type = ChartSelection.NATAL

        # Verify second session unaffected
        assert session2.chart_type is None
        assert session1 is not session2


class TestSessionServiceCleanup:
    """Test suite for session cleanup and privacy-first data deletion."""

    @pytest.mark.asyncio
    async def test_clear_session_removes_user_session(self):
        """Test that clear_session deletes all user data."""
        service = SessionService()
        user_id = 12345

        # Create session with data
        session = await service.get_or_create_session(user_id)
        session.chart_type = ChartSelection.COMPOSITE

        # Clear session
        await service.clear_session(user_id)

        # Verify session is gone - new session should be created
        new_session = await service.get_or_create_session(user_id)
        assert new_session.chart_type is None
        # Should be a different session object
        assert new_session is not session

    @pytest.mark.asyncio
    async def test_clear_session_idempotent(self):
        """Test that clearing non-existent session doesn't raise error."""
        service = SessionService()
        user_id = 99999

        # Clear session that doesn't exist (should not raise error)
        await service.clear_session(user_id)

        # Verify no session exists
        # (Would create new one if we called get_or_create_session)

    @pytest.mark.asyncio
    async def test_clear_session_only_affects_target_user(self):
        """Test that clearing one user's session doesn't affect others."""
        service = SessionService()
        user_id_1 = 12345
        user_id_2 = 67890

        # Create sessions for two users
        session1 = await service.get_or_create_session(user_id_1)
        session2 = await service.get_or_create_session(user_id_2)

        session1.chart_type = ChartSelection.NATAL
        session2.chart_type = ChartSelection.COMPOSITE

        # Clear first user's session
        await service.clear_session(user_id_1)

        # Verify second user's session intact
        retrieved_session2 = await service.get_or_create_session(user_id_2)
        assert retrieved_session2.chart_type == ChartSelection.COMPOSITE
        assert retrieved_session2 is session2


class TestSessionServiceTimeout:
    """Test suite for session timeout management."""

    @pytest.mark.asyncio
    async def test_set_timeout_changes_timeout_duration(self):
        """Test that set_timeout updates session timeout."""
        service = SessionService()
        user_id = 12345

        # Create session with default timeout
        session = await service.get_or_create_session(user_id)
        assert session.timeout_seconds == 1800  # Default 30 minutes

        # Set custom timeout
        await service.set_timeout(user_id, 3600)  # 60 minutes

        # Verify timeout updated
        session = await service.get_or_create_session(user_id)
        assert session.timeout_seconds == 3600

    @pytest.mark.asyncio
    async def test_get_or_create_session_recreates_expired_session(self):
        """Test that expired session is auto-cleared and recreated."""
        service = SessionService()
        user_id = 12345

        # Create session with very short timeout
        session = await service.get_or_create_session(user_id)
        session.chart_type = ChartSelection.NATAL
        session.timeout_seconds = 0  # Expire immediately

        # Simulate passage of time by manually expiring session
        # (In real scenario, time would pass naturally)
        session.last_updated = datetime(2020, 1, 1)  # Very old timestamp

        # Retrieve session (should auto-recreate due to expiry)
        new_session = await service.get_or_create_session(user_id)

        # New session should be clean
        assert new_session.chart_type is None
        assert new_session is not session

    @pytest.mark.asyncio
    async def test_cleanup_expired_sessions_removes_old_sessions(self):
        """Test that cleanup_expired_sessions removes all expired sessions."""
        service = SessionService()
        user_id_1 = 11111
        user_id_2 = 22222
        user_id_3 = 33333

        # Create three sessions
        session1 = await service.get_or_create_session(user_id_1)
        session2 = await service.get_or_create_session(user_id_2)
        session3 = await service.get_or_create_session(user_id_3)

        # Expire first two sessions
        session1.last_updated = datetime(2020, 1, 1)
        session2.last_updated = datetime(2020, 1, 1)

        # Cleanup expired sessions
        cleaned_count = await service.cleanup_expired_sessions()

        # Verify two sessions cleaned
        assert cleaned_count == 2

        # Verify session3 still exists (not expired)
        retrieved_session3 = await service.get_or_create_session(user_id_3)
        assert retrieved_session3 is session3

    @pytest.mark.asyncio
    async def test_cleanup_expired_sessions_no_sessions(self):
        """Test that cleanup with no sessions returns zero."""
        service = SessionService()

        cleaned_count = await service.cleanup_expired_sessions()

        assert cleaned_count == 0

    @pytest.mark.asyncio
    async def test_cleanup_expired_sessions_all_active(self):
        """Test that cleanup with all active sessions returns zero."""
        service = SessionService()
        user_id_1 = 11111
        user_id_2 = 22222

        # Create two active sessions
        await service.get_or_create_session(user_id_1)
        await service.get_or_create_session(user_id_2)

        # Cleanup (should find no expired sessions)
        cleaned_count = await service.cleanup_expired_sessions()

        assert cleaned_count == 0


class TestSessionServiceSingleton:
    """Test suite for singleton instance management."""

    def test_get_session_service_returns_singleton(self):
        """Test that get_session_service returns same instance every time."""
        service1 = get_session_service()
        service2 = get_session_service()

        assert service1 is service2

    @pytest.mark.asyncio
    async def test_singleton_maintains_state_across_calls(self):
        """Test that singleton instance maintains state between calls."""
        service1 = get_session_service()
        user_id = 55555

        # Create session via first reference
        session1 = await service1.get_or_create_session(user_id)
        session1.chart_type = ChartSelection.NATAL

        # Get service again and retrieve session
        service2 = get_session_service()
        session2 = await service2.get_or_create_session(user_id)

        # Should be the same session with same data
        assert session2.chart_type == ChartSelection.NATAL
        assert session1 is session2


class TestSessionServiceEdgeCases:
    """Test suite for edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_session_service_handles_zero_user_id(self):
        """Test that service handles user_id=0 (edge case)."""
        service = SessionService()
        user_id = 0

        session = await service.get_or_create_session(user_id)

        assert session.user_id == 0

    @pytest.mark.asyncio
    async def test_session_service_handles_negative_user_id(self):
        """Test that service handles negative user IDs."""
        service = SessionService()
        user_id = -12345

        session = await service.get_or_create_session(user_id)

        assert session.user_id == -12345

    @pytest.mark.asyncio
    async def test_set_timeout_creates_session_if_not_exists(self):
        """Test that set_timeout creates session if user doesn't have one."""
        service = SessionService()
        user_id = 88888

        # Set timeout for non-existent session (should create it)
        await service.set_timeout(user_id, 7200)

        # Verify session created with custom timeout
        session = await service.get_or_create_session(user_id)
        assert session.timeout_seconds == 7200

    @pytest.mark.asyncio
    async def test_concurrent_session_access_same_user(self):
        """Test that concurrent access to same user session is safe."""
        service = SessionService()
        user_id = 77777

        # Concurrent access to same user session
        session1, session2 = await asyncio.gather(
            service.get_or_create_session(user_id), service.get_or_create_session(user_id)
        )

        # Both should be the same session
        assert session1 is session2
        assert session1.user_id == user_id
