"""Validation error models for user input handling."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ValidationError:
    """Represents a validation error with field context and remediation guidance.

    Attributes:
        field_name: Name of the field that failed validation (e.g., 'birth_date', 'location')
        message: Human-readable error message explaining what went wrong
        remediation: Guidance on how to correct the input (e.g., 'Please enter date in DD.MM.YYYY format')
        user_input: Optional original input that caused the error
    """

    field_name: str
    message: str
    remediation: str
    user_input: Optional[str] = None

    def __str__(self) -> str:
        """Return formatted error message for display to user."""
        return f"{self.message}\n\n{self.remediation}"
