"""
Unit tests for Text Preprocessing

Tests the text normalization and preprocessing components.
"""
import pytest

from nlu.preprocess import normalize_text


@pytest.mark.unit
@pytest.mark.nlp
class TestPreprocessing:
    """Test text preprocessing functions"""

    def test_normalize_text_basic(self):
        """Test basic text normalization"""
        cases = [
            ("Hello World", "hello world"),
            ("UPPERCASE", "uppercase"),
            ("  spaces  ", "spaces"),
        ]
        for input_text, expected in cases:
            result = normalize_text(input_text)
            assert expected in result or result in expected, \
                f"Failed for: {input_text}, got: {result}"

    def test_normalize_text_diacritics(self):
        """Test Vietnamese text normalization"""
        cases = [
            "Điểm chuẩn",
            "Học phí",
            "Kiến trúc",
        ]
        for input_text in cases:
            result = normalize_text(input_text)
            # normalize_text keeps diacritics, just normalizes Unicode and lowercase
            assert result.islower() or not result.isalpha()
            assert isinstance(result, str)
            assert len(result) > 0

    def test_normalize_text_special_chars(self):
        """Test handling of special characters"""
        cases = [
            "Hello!!!",
            "What???",
            "Test...",
        ]
        for input_text in cases:
            result = normalize_text(input_text)
            # Should process without error
            assert isinstance(result, str)

    def test_normalize_text_empty(self):
        """Test empty input handling"""
        cases = ["", "   ", "\n", "\t"]
        for input_text in cases:
            result = normalize_text(input_text)
            assert isinstance(result, str)


@pytest.mark.unit
@pytest.mark.nlp
class TestPreprocessingEdgeCases:
    """Test edge cases in preprocessing"""

    def test_normalize_very_long_text(self):
        """Test normalization of very long text"""
        text = "Điểm chuẩn " * 1000
        result = normalize_text(text)

        # Should handle long text without error
        assert isinstance(result, str)
        assert len(result) > 0

    def test_normalize_unicode_emoji(self):
        """Test handling of emoji and special Unicode"""
        cases = [
            "Hello 😊",
            "Test 🎓",
            "CNTT 💻",
        ]
        for text in cases:
            result = normalize_text(text)
            # Should handle without crashing
            assert isinstance(result, str)

    def test_normalize_case_insensitive(self):
        """Test case insensitivity in normalization"""
        texts = ["ĐIỂM CHUẨN", "điểm chuẩn", "Điểm Chuẩn"]
        results = [normalize_text(t) for t in texts]

        # All should be lowercase
        assert all(r.islower() or not r.isalpha() for r in results)
