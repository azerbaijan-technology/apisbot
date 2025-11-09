"""Date and time data models for birth information."""

from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Optional


@dataclass
class DateTimeData:
    """Represents validated date and time data for birth information.

    Attributes:
        birth_date: Birth date (validated, not in future, not too far in past)
        birth_time: Birth time (24-hour format, optional for some chart types)
        display_date: Human-readable date format for display
        display_time: Human-readable time format for display
    """

    birth_date: date
    birth_time: Optional[time] = None
    display_date: Optional[str] = None
    display_time: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate date constraints and set display formats."""
        # Validate date is not in the future
        if self.birth_date > date.today():
            raise ValueError("Birth date cannot be in the future")

        # Validate date is not unreasonably old (e.g., > 200 years ago)
        min_year = date.today().year - 200
        if self.birth_date.year < min_year:
            raise ValueError(f"Birth date must be after year {min_year}")

        # Set display formats if not provided
        if self.display_date is None:
            self.display_date = self.birth_date.strftime("%d.%m.%Y")

        if self.birth_time and self.display_time is None:
            self.display_time = self.birth_time.strftime("%H:%M")

    @property
    def datetime(self) -> Optional[datetime]:
        """Combine date and time into a datetime object if time is available."""
        if self.birth_time:
            return datetime.combine(self.birth_date, self.birth_time)
        return None
