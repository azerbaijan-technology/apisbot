"""User session models for tracking conversation state."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from .birth_data import BirthData
from .chart_selection import ChartSelection


@dataclass
class UserSession:
    """Tracks user's conversation state and collected data.

    Privacy-first design: Session data must be cleared after chart generation or timeout.
    Default timeout: 30 minutes (per constitution principle IV).

    Attributes:
        user_id: Telegram user ID
        chart_type: Selected chart type (Natal or Composite)
        person1_data: First person's birth data (required for all chart types)
        person2_data: Second person's birth data (required only for Composite charts)
        created_at: Session creation timestamp
        last_updated: Last activity timestamp
        timeout_seconds: Session timeout duration (default: 1800 = 30 minutes)
    """

    user_id: int
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    chart_type: Optional[ChartSelection] = None
    person1_data: Optional[BirthData] = None
    person2_data: Optional[BirthData] = None
    timeout_seconds: int = 1800  # 30 minutes default

    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_updated = datetime.now()

    def is_expired(self) -> bool:
        """Check if session has exceeded timeout.

        Returns:
            True if session is older than timeout_seconds
        """
        elapsed = (datetime.now() - self.last_updated).total_seconds()
        return elapsed > self.timeout_seconds

    def is_complete(self) -> bool:
        """Check if session has all required data for chart generation.

        Returns:
            True if chart type is selected and required birth data is complete
        """
        if not self.chart_type or not self.person1_data:
            return False

        # For natal chart, only person1_data is needed
        if self.chart_type == ChartSelection.NATAL:
            return self.person1_data.is_complete()

        # For composite chart, both person1_data and person2_data are needed
        if self.chart_type == ChartSelection.COMPOSITE:
            return self.person1_data.is_complete() and (
                self.person2_data is not None and self.person2_data.is_complete()
            )

        return False

    def clear(self) -> None:
        """Clear all session data (privacy-first: delete all user data).

        Called after:
        - Chart generation completion
        - User cancels conversation
        - Session timeout
        """
        self.chart_type = None
        self.person1_data = None
        self.person2_data = None
        self.last_updated = datetime.now()
