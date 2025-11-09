from dataclasses import dataclass
from datetime import date, time
from typing import Optional


@dataclass
class BirthData:
    """Birth information for natal chart generation.

    Stores user-provided birth data collected during the conversation flow.
    Coordinates and timezone are filled by kerykeion after geocoding.

    Validation rules:
    - Name: 1-100 characters with at least one letter
    - Date: Within 200 years, not in future, valid calendar date
    - Time: Valid 24-hour format (00:00-23:59)
    - Location: Recognizable city name with geocoding coordinates
    """

    name: str
    birth_date: date
    birth_time: time
    location: str  # City name (e.g., "New York")

    # Filled by kerykeion after geocoding
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = None
    nation: str = " "

    def validate_name(self) -> bool:
        """Validate name is 1-100 characters with at least one letter."""
        if not self.name or len(self.name) < 1 or len(self.name) > 100:
            return False
        return any(c.isalpha() for c in self.name)

    def validate_date(self) -> bool:
        """Validate birth date is within 200 years and not in future.

        Edge cases handled:
        - Future dates rejected
        - Dates > 200 years ago rejected
        - Invalid calendar dates (Feb 30) rejected by datetime.date itself
        """
        from datetime import timedelta

        today = date.today()
        min_date = today - timedelta(days=200 * 365)

        return min_date <= self.birth_date <= today

    def validate_time(self) -> bool:
        """Validate birth time is in valid 24-hour format.

        Returns:
            True if time is valid (00:00-23:59), False otherwise
        """
        return 0 <= self.birth_time.hour <= 23 and 0 <= self.birth_time.minute <= 59

    def validate_location(self) -> bool:
        """Validate location has geocoding coordinates.

        Returns:
            True if latitude, longitude, and timezone are set (location was geocoded successfully)
        """
        return all([self.latitude is not None, self.longitude is not None, self.timezone is not None])

    def is_complete(self) -> bool:
        """Check if all required fields are filled and valid.

        Returns:
            True if all validations pass and location is geocoded
        """
        return all([self.validate_name(), self.validate_date(), self.validate_time(), self.validate_location()])
