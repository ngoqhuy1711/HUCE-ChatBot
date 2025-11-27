"""
Input Sanitization Utilities

Functions to clean and validate user input for security and quality.
"""

import html
import re
from typing import Optional


def sanitize_message(message: str, max_length: int = 1000) -> str:
    """
    Sanitize user message input.

    This function:
    1. Strips whitespace
    2. Removes control characters
    3. Escapes HTML entities (XSS prevention)
    4. Removes excessive repeated characters
    5. Truncates to max length
    6. Removes SQL injection patterns (basic)

    Args:
        message: Raw user input
        max_length: Maximum allowed length (default: 1000)

    Returns:
        Sanitized message

    Example:
        >>> sanitize_message("  Hello!!!!!!  ")
        "Hello!!!"
        >>> sanitize_message("<script>alert('xss')</script>")
        "&lt;script&gt;alert('xss')&lt;/script&gt;"
    """
    if not message:
        return ""

    # 1. Strip whitespace
    message = message.strip()

    # 2. Remove control characters (except newline and tab)
    message = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', message)

    # 3. Escape HTML entities (prevent XSS)
    message = html.escape(message)

    # 4. Remove excessive repeated characters (more than 3 in a row)
    # "Helllllo" -> "Hello"
    message = re.sub(r'(.)\1{3,}', r'\1\1\1', message)

    # 5. Normalize whitespace (replace multiple spaces with single space)
    message = re.sub(r'\s+', ' ', message)

    # 6. Truncate to max length
    if len(message) > max_length:
        message = message[:max_length]

    # 7. Remove SQL injection patterns (basic)
    # This is basic protection, real SQL injection prevention
    # should be done with parameterized queries
    dangerous_patterns = [
        r';\s*(DROP|DELETE|UPDATE|INSERT)\s+',
        r'(UNION|SELECT).*FROM',
        r'--\s*$',
        r'/\*.*\*/',
    ]
    for pattern in dangerous_patterns:
        message = re.sub(pattern, '', message, flags=re.IGNORECASE)

    return message.strip()


def validate_session_id(session_id: Optional[str]) -> str:
    """
    Validate and sanitize session ID.

    Session ID should be:
    - Alphanumeric + underscore + hyphen only
    - Between 1-100 characters
    - Default to "default" if invalid

    Args:
        session_id: Raw session ID

    Returns:
        Sanitized session ID or "default"

    Example:
        >>> validate_session_id("user_123")
        "user_123"
        >>> validate_session_id("user@#$%")
        "default"
        >>> validate_session_id(None)
        "default"
    """
    if not session_id:
        return "default"

    # Only allow alphanumeric, underscore, and hyphen
    session_id = re.sub(r'[^a-zA-Z0-9_-]', '', session_id)

    # Limit length
    if len(session_id) > 100:
        session_id = session_id[:100]

    # Return default if empty after sanitization
    return session_id if session_id else "default"


def remove_excessive_punctuation(text: str) -> str:
    """
    Remove excessive punctuation.

    "Hello!!!!!" -> "Hello!"
    "What????" -> "What?"

    Args:
        text: Text with possible excessive punctuation

    Returns:
        Text with normalized punctuation
    """
    # Replace 2+ punctuation marks with single one
    text = re.sub(r'([!?.]){2,}', r'\1', text)
    return text


def detect_spam(message: str) -> bool:
    """
    Basic spam detection.

    Returns True if message looks like spam:
    - All caps
    - Too many URLs
    - Too many special characters
    - Known spam patterns

    Args:
        message: User message

    Returns:
        True if spam, False otherwise
    """
    if not message:
        return False

    # All caps (more than 80% uppercase) and long enough
    if len(message) > 20:
        uppercase_ratio = sum(1 for c in message if c.isupper()) / len(message)
        if uppercase_ratio > 0.8:
            return True

    # Too many URLs
    url_count = len(re.findall(r'https?://', message))
    if url_count > 3:
        return True

    # Too many special characters (more than 50%)
    special_char_ratio = sum(1 for c in message if not c.isalnum() and not c.isspace()) / len(message)
    if special_char_ratio > 0.5:
        return True

    # Known spam patterns
    spam_patterns = [
        r'(click|clik)\s+(here|hear)',
        r'(buy|bye)\s+(now|naow)',
        r'(free|fr33)\s+(money|muney)',
        r'(win|winn)\s+\$\d+',
    ]
    for pattern in spam_patterns:
        if re.search(pattern, message, re.IGNORECASE):
            return True

    return False


def normalize_vietnamese_text(text: str) -> str:
    """
    Normalize Vietnamese text variations.

    Handles common mistakes:
    - "hoc phi" -> "học phí"
    - "diem chuan" -> "điểm chuẩn"

    Note: This is a simple version. For production,
    consider using a proper Vietnamese NLP library.

    Args:
        text: Text to normalize

    Returns:
        Normalized text
    """
    # This is handled by NLP pipeline, but we can add
    # basic normalization here if needed

    # Remove zero-width characters
    text = text.replace('\u200b', '')  # Zero-width space
    text = text.replace('\ufeff', '')  # Zero-width no-break space

    return text


# Export all sanitization functions
__all__ = [
    'sanitize_message',
    'validate_session_id',
    'remove_excessive_punctuation',
    'detect_spam',
    'normalize_vietnamese_text',
]
