import re
from datetime import date, time, timedelta


def parse_date(date_str: str) -> date:
    """Parse flexible date formats into a date object.

    Supported formats:
    - YYYY-MM-DD (e.g., "1990-05-15")
    - DD/MM/YYYY (e.g., "15/05/1990")
    - DD-MM-YYYY (e.g., "15-05-1990")
    - Month DD, YYYY (e.g., "May 15, 1990")
    - DD Month YYYY (e.g., "15 May 1990")

    Args:
        date_str: String representation of a date

    Returns:
        Parsed date object

    Raises:
        ValueError: If date format is invalid or date is out of valid range
    """
    date_str = date_str.strip()

    # Try YYYY-MM-DD format
    if re.match(r"^\d{4}-\d{1,2}-\d{1,2}$", date_str):
        parts = date_str.split("-")
        parsed_date = date(int(parts[0]), int(parts[1]), int(parts[2]))

    # Try DD/MM/YYYY or DD-MM-YYYY format
    elif re.match(r"^\d{1,2}[/-]\d{1,2}[/-]\d{4}$", date_str):
        parts = re.split(r"[/-]", date_str)
        parsed_date = date(int(parts[2]), int(parts[1]), int(parts[0]))

    # Try "Month DD, YYYY" format
    elif re.match(r"^[A-Za-z]+\s+\d{1,2},?\s+\d{4}$", date_str):
        # Use strptime for month name parsing
        from datetime import datetime

        parsed_date = datetime.strptime(date_str.replace(",", ""), "%B %d %Y").date()

    # Try "DD Month YYYY" format
    elif re.match(r"^\d{1,2}\s+[A-Za-z]+\s+\d{4}$", date_str):
        from datetime import datetime

        parsed_date = datetime.strptime(date_str, "%d %B %Y").date()

    else:
        raise ValueError(
            "Invalid date format. Please use one of: YYYY-MM-DD, DD/MM/YYYY, "
            "or 'Month DD, YYYY' (e.g., '1990-05-15' or 'May 15, 1990')"
        )

    # Validate range (150 years ago to today)
    today = date.today()
    min_date = today - timedelta(days=150 * 365)

    if parsed_date > today:
        raise ValueError("Birth date cannot be in the future")

    if parsed_date < min_date:
        raise ValueError("Birth date cannot be more than 150 years ago")

    return parsed_date


def parse_time(time_str: str) -> time:
    """Parse flexible time formats into a time object.

    Supported formats:
    - HH:MM (24-hour, e.g., "14:30")
    - HH (hour only, defaults to :00, e.g., "14" becomes "14:00")
    - HH:MM AM/PM (12-hour, e.g., "2:30 PM")
    - HH AM/PM (12-hour with hour only, e.g., "2 PM")

    Args:
        time_str: String representation of a time

    Returns:
        Parsed time object

    Raises:
        ValueError: If time format is invalid
    """
    time_str = time_str.strip()

    # Try 24-hour format HH:MM
    if re.match(r"^\d{1,2}:\d{2}$", time_str):
        parts = time_str.split(":")
        hour, minute = int(parts[0]), int(parts[1])

        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("Invalid time: hours must be 0-23, minutes must be 0-59")

        return time(hour, minute)

    # Try hour only (24-hour)
    elif re.match(r"^\d{1,2}$", time_str):
        hour = int(time_str)

        if not (0 <= hour <= 23):
            raise ValueError("Invalid hour: must be 0-23")

        return time(hour, 0)

    # Try 12-hour format with AM/PM
    elif re.match(r"^\d{1,2}(:\d{2})?\s*[AaPp][Mm]$", time_str, re.IGNORECASE):
        # Extract hour, minute, and AM/PM
        match = re.match(r"^(\d{1,2})(?::(\d{2}))?\s*([AaPp][Mm])$", time_str, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid time format")

        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        period = match.group(3).upper()

        # Validate
        if not (1 <= hour <= 12 and 0 <= minute <= 59):
            raise ValueError("Invalid time: hours must be 1-12 for AM/PM format, minutes must be 0-59")

        # Convert to 24-hour
        if period == "AM":
            hour = 0 if hour == 12 else hour
        else:  # PM
            hour = 12 if hour == 12 else hour + 12

        return time(hour, minute)

    else:
        raise ValueError(
            "Invalid time format. Please use one of: HH:MM (24-hour), "
            "HH (hour only), or HH:MM AM/PM (12-hour). Examples: '14:30', '14', '2:30 PM'"
        )


def suggest_date_format(invalid_input: str) -> str:
    """Generate helpful suggestion for invalid date input."""
    suggestions = [
        "YYYY-MM-DD (e.g., 1990-05-15)",
        "DD/MM/YYYY (e.g., 15/05/1990)",
        "Month DD, YYYY (e.g., May 15, 1990)",
    ]
    return f"Invalid date format: '{invalid_input}'. Please try:\n" + "\n".join(f"  • {s}" for s in suggestions)


def suggest_time_format(invalid_input: str) -> str:
    """Generate helpful suggestion for invalid time input."""
    suggestions = [
        "HH:MM (24-hour, e.g., 14:30)",
        "HH:MM AM/PM (12-hour, e.g., 2:30 PM)",
        "HH (hour only, e.g., 14 or 2 PM)",
    ]
    return f"Invalid time format: '{invalid_input}'. Please try:\n" + "\n".join(f"  • {s}" for s in suggestions)
