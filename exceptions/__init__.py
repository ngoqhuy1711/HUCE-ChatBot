"""
Custom Exceptions for Chatbot HUCE
====================
Exception Hierarchy:

All custom exceptions inherit from ChatbotException base class.
This module defines the exception hierarchy for the chatbot system.

"""
from typing import Optional, Dict, Any


class ChatbotException(Exception):
    """Base exception for all chatbot-specific errors."""

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"{self.error_code}: {self.message}"

    def __str__(self) -> str:
        """String representation of the exception."""
        if self.details:
            return f"{self.error_code}: {self.message} (Details: {self.details})"
        return f"{self.error_code}: {self.message}"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary for API responses.

        Returns:
            Dictionary with error information
        """
        return {
            "error_code": self.error_code,
            "error_message": self.message,
            "details": self.details,
        }

    def __init__(
            self,
            message: str,
            error_code: str = "CHATBOT_ERROR",
            details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize ChatbotException.

        Args:
            message: Error message for humans
            error_code: Error code for machines (default: CHATBOT_ERROR)
            details: Additional context (optional)
        """
        super().__init__(message)
        self.details = details or {}
        self.error_code = error_code
        self.message = message


# Import all exception classes for easy access
from .nlp_exceptions import (
    NLPException,
    IntentNotFoundError,
    EntityExtractionError,
    ContextError,
    PreprocessingError,
)
from .data_exceptions import (
    DataException,
    DataNotFoundError,
    CSVLoadError,
    InvalidMajorError,
    DataValidationError,
)
from .api_exceptions import (
    APIException,
    ValidationError,
    RateLimitError,
    AuthenticationError,
    ResourceNotFoundError,
)

# Export all exceptions
__all__ = [
    # Base
    "ChatbotException",
    # NLP
    "NLPException",
    "IntentNotFoundError",
    "EntityExtractionError",
    "ContextError",
    "PreprocessingError",
    # Data
    "DataException",
    "DataNotFoundError",
    "CSVLoadError",
    "InvalidMajorError",
    "DataValidationError",
    # API
    "APIException",
    "ValidationError",
    "RateLimitError",
    "AuthenticationError",
    "ResourceNotFoundError",
]
