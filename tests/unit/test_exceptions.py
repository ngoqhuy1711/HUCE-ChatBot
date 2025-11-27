"""
Unit tests for Custom Exceptions

Tests the exception hierarchy and functionality.
"""
import pytest

from exceptions import (
    ChatbotException,
    IntentNotFoundError,
    EntityExtractionError,
    ContextError,
    DataNotFoundError,
    CSVLoadError,
    InvalidMajorError,
    ValidationError,
    RateLimitError,
)


@pytest.mark.unit
class TestBaseException:
    """Test ChatbotException base class"""

    def test_basic_exception(self):
        """Test basic exception creation"""
        exc = ChatbotException("Test error")
        assert exc.message == "Test error"
        assert exc.error_code == "CHATBOT_ERROR"
        assert exc.details == {}

    def test_exception_with_code(self):
        """Test exception with custom error code"""
        exc = ChatbotException("Test error", error_code="CUSTOM_ERROR")
        assert exc.error_code == "CUSTOM_ERROR"

    def test_exception_with_details(self):
        """Test exception with details"""
        details = {"key": "value", "count": 42}
        exc = ChatbotException("Test error", details=details)
        assert exc.details == details

    def test_exception_to_dict(self):
        """Test converting exception to dictionary"""
        exc = ChatbotException(
            "Test error",
            error_code="TEST_ERROR",
            details={"field": "test"}
        )
        data = exc.to_dict()

        assert data["error_code"] == "TEST_ERROR"
        assert data["error_message"] == "Test error"
        assert data["details"]["field"] == "test"

    def test_exception_str(self):
        """Test string representation"""
        exc = ChatbotException("Test error", error_code="TEST_CODE")
        assert "TEST_CODE" in str(exc)
        assert "Test error" in str(exc)


@pytest.mark.unit
class TestNLPExceptions:
    """Test NLP-related exceptions"""

    def test_intent_not_found(self):
        """Test IntentNotFoundError"""
        exc = IntentNotFoundError(
            confidence=0.25,
            detected_intent="fallback",
            original_message="test message"
        )

        assert exc.error_code == "INTENT_NOT_FOUND"
        assert exc.details["confidence"] == 0.25
        assert exc.details["detected_intent"] == "fallback"

    def test_entity_extraction_error(self):
        """Test EntityExtractionError"""
        exc = EntityExtractionError(
            original_message="test",
            expected_entities=["TEN_NGANH"],
            found_entities=[]
        )

        assert exc.error_code == "ENTITY_EXTRACTION_ERROR"
        assert exc.details["expected_entities"] == ["TEN_NGANH"]

    def test_context_error(self):
        """Test ContextError"""
        exc = ContextError(
            session_id="test_123",
            context_data={"key": "value"}
        )

        assert exc.error_code == "CONTEXT_ERROR"
        assert exc.details["session_id"] == "test_123"


@pytest.mark.unit
class TestDataExceptions:
    """Test data-related exceptions"""

    def test_data_not_found(self):
        """Test DataNotFoundError"""
        exc = DataNotFoundError(
            data_type="standard_score",
            query_params={"major": "test"}
        )

        assert exc.error_code == "DATA_NOT_FOUND"
        assert exc.details["data_type"] == "standard_score"

    def test_csv_load_error(self):
        """Test CSVLoadError"""
        exc = CSVLoadError(
            file_path="/path/to/file.csv",
            error_details="File not found"
        )

        assert exc.error_code == "CSV_LOAD_ERROR"
        assert exc.details["file_path"] == "/path/to/file.csv"

    def test_invalid_major_error(self):
        """Test InvalidMajorError"""
        exc = InvalidMajorError(
            major_name="InvalidMajor",
            suggestions=["Kiến trúc", "CNTT"]
        )

        assert exc.error_code == "INVALID_MAJOR"
        assert len(exc.details["suggestions"]) == 2


@pytest.mark.unit
class TestAPIExceptions:
    """Test API-related exceptions"""

    def test_validation_error(self):
        """Test ValidationError"""
        exc = ValidationError(
            field="message",
            value="",
            constraint="not empty"
        )

        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.status_code == 422
        assert exc.details["field"] == "message"

    def test_rate_limit_error(self):
        """Test RateLimitError"""
        exc = RateLimitError(
            limit=100,
            window="60s",
            retry_after=30
        )

        assert exc.error_code == "RATE_LIMIT_ERROR"
        assert exc.status_code == 429
        assert exc.details["limit"] == 100

    def test_api_exception_to_dict(self):
        """Test APIException includes status_code in dict"""
        exc = ValidationError("Test error")
        data = exc.to_dict()

        assert "status_code" in data
        assert data["status_code"] == 422


@pytest.mark.unit
class TestExceptionInheritance:
    """Test exception inheritance"""

    def test_intent_error_is_nlp_exception(self):
        """Test IntentNotFoundError inherits from NLPException"""
        exc = IntentNotFoundError()
        assert isinstance(exc, ChatbotException)

    def test_data_error_is_chatbot_exception(self):
        """Test DataNotFoundError inherits from ChatbotException"""
        exc = DataNotFoundError()
        assert isinstance(exc, ChatbotException)

    def test_api_error_is_chatbot_exception(self):
        """Test ValidationError inherits from ChatbotException"""
        exc = ValidationError()
        assert isinstance(exc, ChatbotException)

    def test_catch_all_chatbot_exceptions(self):
        """Test catching all custom exceptions"""
        exceptions = [
            IntentNotFoundError(),
            DataNotFoundError(),
            ValidationError(),
        ]

        for exc in exceptions:
            try:
                raise exc
            except ChatbotException as e:
                assert isinstance(e, ChatbotException)


@pytest.mark.unit
class TestExceptionMessages:
    """Test exception messages"""

    def test_default_messages(self):
        """Test default error messages are in Vietnamese"""
        exc1 = IntentNotFoundError()
        exc2 = DataNotFoundError()
        exc3 = ValidationError()

        # Should have Vietnamese messages
        assert "không" in exc1.message.lower() or "khong" in exc1.message.lower()
        assert "không" in exc2.message.lower() or "khong" in exc2.message.lower()
        assert "không" in exc3.message.lower() or "khong" in exc3.message.lower()

    def test_custom_messages(self):
        """Test custom error messages"""
        custom_msg = "Custom error message"
        exc = IntentNotFoundError(message=custom_msg)
        assert exc.message == custom_msg
