from dataclasses import dataclass
from datetime import date, time


@dataclass
class BirthData:
    """Birth information for natal chart generation.

    Stores user-provided birth data collected during the conversation flow.
    Coordinates and timezone are filled by kerykeion after geocoding.
    """

    name: str
    birth_date: date
    birth_time: time
    location: str  # City name (e.g., "New York")

    # Filled by kerykeion after geocoding
    latitude: float | None = None
    longitude: float | None = None
    timezone: str | None = None

    def validate_name(self) -> bool:
        """Validate name is 1-100 characters with at least one letter."""
        if not self.name or len(self.name) < 1 or len(self.name) > 100:
            return False
        return any(c.isalpha() for c in self.name)

    def validate_date(self) -> bool:
        """Validate birth date is within 150 years and not in future."""
        from datetime import timedelta

        today = date.today()
        min_date = today - timedelta(days=150 * 365)

        return min_date <= self.birth_date <= today
