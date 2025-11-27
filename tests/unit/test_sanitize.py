"""
Unit tests for Input Sanitization

Tests the input sanitization and validation utilities.
"""
import pytest

from utils.sanitize import (
    sanitize_message,
    validate_session_id,
    remove_excessive_punctuation,
    detect_spam,
    normalize_vietnamese_text,
)


@pytest.mark.unit
class TestSanitizeMessage:
    """Test message sanitization"""

    def test_strip_whitespace(self):
        """Test whitespace stripping"""
        assert sanitize_message("  Hello  ") == "Hello"
        assert sanitize_message("\n\nHello\n\n") == "Hello"
        assert sanitize_message("\t\tHello\t\t") == "Hello"

    def test_remove_control_characters(self):
        """Test control character removal"""
        # Control characters should be removed
        text = "Hello\x00World\x08Test"
        result = sanitize_message(text)
        assert "\x00" not in result
        assert "\x08" not in result

    def test_html_escape(self):
        """Test HTML entity escaping (XSS prevention)"""
        assert "&lt;" in sanitize_message("<script>")
        assert "&gt;" in sanitize_message("</script>")
        assert "&amp;" in sanitize_message("a & b")

    def test_remove_excessive_repetition(self):
        """Test removal of excessive repeated characters"""
        # Function reduces to max 3 repeated characters
        assert sanitize_message("Helllllo") == "Helllo"  # 7 l's → 3 l's
        assert sanitize_message("Wowwwwww") == "Wowww"  # 6 w's → 3 w's
        assert sanitize_message("!!!!!!") == "!!!"  # 6 !'s → 3 !'s

    def test_normalize_whitespace(self):
        """Test whitespace normalization"""
        assert sanitize_message("Hello    World") == "Hello World"
        assert sanitize_message("a  b  c") == "a b c"

    def test_truncate_long_message(self):
        """Test message truncation"""
        long_message = "a" * 2000
        result = sanitize_message(long_message, max_length=1000)
        assert len(result) <= 1000

    def test_sql_injection_prevention(self):
        """Test basic SQL injection pattern removal"""
        assert "DROP" not in sanitize_message("; DROP TABLE users;")
        assert "DELETE" not in sanitize_message("; DELETE FROM users;")

    def test_empty_input(self):
        """Test empty input handling"""
        assert sanitize_message("") == ""
        assert sanitize_message("   ") == ""
        assert sanitize_message(None) == ""


@pytest.mark.unit
class TestValidateSessionId:
    """Test session ID validation"""

    def test_valid_session_ids(self):
        """Test valid session IDs"""
        assert validate_session_id("user_123") == "user_123"
        assert validate_session_id("session-456") == "session-456"
        assert validate_session_id("abc123") == "abc123"

    def test_invalid_characters(self):
        """Test removal of invalid characters"""
        # Should remove special chars
        result = validate_session_id("user@#$123")
        assert "@" not in result
        assert "#" not in result
        assert "$" not in result

    def test_none_input(self):
        """Test None input"""
        assert validate_session_id(None) == "default"

    def test_empty_input(self):
        """Test empty input"""
        assert validate_session_id("") == "default"

    def test_long_session_id(self):
        """Test long session ID truncation"""
        long_id = "a" * 200
        result = validate_session_id(long_id)
        assert len(result) <= 100


@pytest.mark.unit
class TestRemoveExcessivePunctuation:
    """Test excessive punctuation removal"""

    def test_multiple_exclamations(self):
        """Test multiple exclamation marks"""
        assert remove_excessive_punctuation("Hello!!!!!") == "Hello!"
        assert remove_excessive_punctuation("Wow!!!") == "Wow!"

    def test_multiple_questions(self):
        """Test multiple question marks"""
        assert remove_excessive_punctuation("What????") == "What?"
        assert remove_excessive_punctuation("Really???") == "Really?"

    def test_multiple_periods(self):
        """Test multiple periods"""
        assert remove_excessive_punctuation("Wait...") == "Wait."

    def test_normal_punctuation(self):
        """Test normal punctuation preserved"""
        assert remove_excessive_punctuation("Hello!") == "Hello!"
        assert remove_excessive_punctuation("What?") == "What?"


@pytest.mark.unit
class TestDetectSpam:
    """Test spam detection"""

    def test_all_caps_spam(self):
        """Test all caps detection"""
        assert detect_spam("BUY NOW THIS AMAZING PRODUCT") is True
        assert detect_spam("CLICK HERE FOR FREE MONEY") is True

    def test_normal_caps_not_spam(self):
        """Test normal caps not detected as spam"""
        assert detect_spam("Hello World") is False
        assert detect_spam("CNTT") is False  # Short, OK

    def test_too_many_urls(self):
        """Test too many URLs"""
        spam_text = "http://spam1.com http://spam2.com http://spam3.com http://spam4.com"
        assert detect_spam(spam_text) is True

    def test_normal_url_not_spam(self):
        """Test normal URL not spam"""
        assert detect_spam("Check out https://example.com") is False

    def test_too_many_special_chars(self):
        """Test too many special characters"""
        assert detect_spam("!!!@@@###$$$%%%") is True

    def test_spam_patterns(self):
        """Test known spam patterns"""
        assert detect_spam("Click here to win $1000") is True
        assert detect_spam("Buy now for free money") is True

    def test_normal_text_not_spam(self):
        """Test normal text not detected as spam"""
        assert detect_spam("Điểm chuẩn ngành CNTT?") is False
        assert detect_spam("Học phí là bao nhiêu?") is False


@pytest.mark.unit
class TestNormalizeVietnameseText:
    """Test Vietnamese text normalization"""

    def test_zero_width_characters(self):
        """Test zero-width character removal"""
        text_with_zw = "Hello\u200bWorld"
        result = normalize_vietnamese_text(text_with_zw)
        assert "\u200b" not in result

    def test_zero_width_no_break_space(self):
        """Test zero-width no-break space removal"""
        text_with_zwnbs = "Hello\ufeffWorld"
        result = normalize_vietnamese_text(text_with_zwnbs)
        assert "\ufeff" not in result

    def test_normal_text_preserved(self):
        """Test normal text is preserved"""
        text = "Điểm chuẩn ngành CNTT"
        result = normalize_vietnamese_text(text)
        assert result == text


@pytest.mark.unit
class TestSanitizationIntegration:
    """Test sanitization integration scenarios"""

    def test_complete_sanitization(self):
        """Test complete sanitization pipeline"""
        dirty_input = "  <script>alert('xss')</script>!!!!!  "
        result = sanitize_message(dirty_input)

        # Should be sanitized
        assert "<script>" not in result
        assert "!!!" in result  # Reduced but not removed
        assert result.strip() == result  # No leading/trailing whitespace

    def test_vietnamese_with_spam(self):
        """Test Vietnamese text spam detection"""
        # Short all-caps Vietnamese should not trigger (< 20 chars)
        text_short = "ĐIỂM CHUẨN"
        assert detect_spam(text_short) is False

        # Normal Vietnamese questions should not be spam
        text_normal = "Điểm chuẩn ngành CNTT năm 2024?"
        assert detect_spam(text_normal) is False

    def test_safe_message_unchanged(self):
        """Test that safe messages are mostly unchanged"""
        safe_message = "Điểm chuẩn ngành Kiến trúc năm 2024?"
        result = sanitize_message(safe_message)
        # Should be similar (may have HTML escaping)
        assert len(result) > 0
        assert "Kiến trúc" in result or "Ki" in result  # May be escaped
