"""Location data models for birth place information."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class LocationData:
    """Represents validated location data for birth place.

    Attributes:
        city: City name (e.g., 'New York', 'London')
        country: Country name (optional, for disambiguation)
        latitude: Latitude coordinate (-90 to 90)
        longitude: Longitude coordinate (-180 to 180)
        timezone: IANA timezone identifier (e.g., 'America/New_York')
        display_name: Full location name for display (e.g., 'New York, United States')
    """

    city: str
    latitude: float
    longitude: float
    timezone: str
    display_name: str
    country: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate coordinate ranges."""
        if not -90 <= self.latitude <= 90:
            raise ValueError(f"Latitude must be between -90 and 90, got {self.latitude}")
        if not -180 <= self.longitude <= 180:
            raise ValueError(f"Longitude must be between -180 and 180, got {self.longitude}")
