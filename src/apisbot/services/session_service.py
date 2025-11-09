"""Session management service for user conversation state.

Framework-agnostic service with no aiogram dependencies.
Fully testable without bot infrastructure.
"""

from typing import Dict

from ..models.session import UserSession


class SessionService:
    """Manages user session lifecycle and data.

    Privacy-first design:
    - Sessions cleared after chart generation
    - Sessions auto-expire after timeout (default: 30 minutes)
    - No persistent storage (in-memory only)

    No aiogram dependencies: Can be tested independently.
    """

    def __init__(self) -> None:
        """Initialize session service with empty session storage."""
        self._sessions: Dict[int, UserSession] = {}

    async def get_or_create_session(self, user_id: int) -> UserSession:
        """Get existing session or create new one for user.

        Args:
            user_id: Telegram user ID

        Returns:
            UserSession for the user (existing or newly created)
        """
        if user_id in self._sessions:
            session = self._sessions[user_id]
            # Check if session expired
            if session.is_expired():
                # Clear expired session and create new one
                await self.clear_session(user_id)
                return await self.get_or_create_session(user_id)
            # Update activity timestamp
            session.update_activity()
            return session

        # Create new session
        session = UserSession(user_id=user_id)
        self._sessions[user_id] = session
        return session

    async def clear_session(self, user_id: int) -> None:
        """Clear all session data for user (privacy-first).

        Called when:
        - Chart generation completes
        - User cancels conversation
        - Session expires

        Args:
            user_id: Telegram user ID
        """
        if user_id in self._sessions:
            del self._sessions[user_id]

    async def set_timeout(self, user_id: int, timeout_seconds: int) -> None:
        """Set custom session timeout for user.

        Args:
            user_id: Telegram user ID
            timeout_seconds: Timeout duration in seconds (default: 1800 = 30 minutes)
        """
        session = await self.get_or_create_session(user_id)
        session.timeout_seconds = timeout_seconds

    async def cleanup_expired_sessions(self) -> int:
        """Remove all expired sessions (privacy cleanup).

        Returns:
            Number of sessions cleaned up
        """
        expired_user_ids = [user_id for user_id, session in self._sessions.items() if session.is_expired()]

        for user_id in expired_user_ids:
            await self.clear_session(user_id)

        return len(expired_user_ids)


# Singleton instance for use across application
_session_service: SessionService | None = None


def get_session_service() -> SessionService:
    """Get singleton SessionService instance.

    Returns:
        Shared SessionService instance
    """
    global _session_service
    if _session_service is None:
        _session_service = SessionService()
    return _session_service
