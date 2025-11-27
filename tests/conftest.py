"""
Pytest configuration and shared fixtures
"""
import pytest
from fastapi.testclient import TestClient

from main import app
from services.nlp_service import get_nlp_service


@pytest.fixture
def test_client():
    """FastAPI test client for API testing"""
    return TestClient(app)


@pytest.fixture
def nlp_service():
    """NLP service instance for testing"""
    return get_nlp_service()


@pytest.fixture
def sample_messages():
    """Sample messages for testing"""
    return {
        "diem_chuan": [
            "Điểm chuẩn ngành Kiến trúc?",
            "Cho mình hỏi điểm chuẩn ngành CNTT",
            "Điểm chuẩn năm 2024",
        ],
        "hoc_phi": [
            "Học phí ngành Xây dựng?",
            "Học phí năm 2025 là bao nhiêu?",
            "Cho mình xin thông tin học phí",
        ],
        "hoc_bong": [
            "Học bổng có gì?",
            "Trường có học bổng không?",
            "Thông tin về học bổng",
        ],
        "nganh_hoc": [
            "Ngành Kiến trúc học những gì?",
            "Giới thiệu ngành CNTT",
            "Thông tin ngành Xây dựng",
        ],
        "fallback": [
            "Xin chào",
            "Hello",
            "asdfghjkl",
        ],
    }


@pytest.fixture
def sample_context():
    """Sample context data for testing"""
    return {
        "empty": {},
        "with_major": {
            "last_intent": "hoi_diem_chuan",
            "last_entities": [
                {"label": "TEN_NGANH", "text": "kiến trúc"}
            ],
            "conversation_history": []
        },
        "with_history": {
            "last_intent": "hoi_diem_chuan",
            "last_entities": [
                {"label": "TEN_NGANH", "text": "kiến trúc"}
            ],
            "conversation_history": [
                {
                    "message": "Điểm chuẩn ngành Kiến trúc?",
                    "intent": "hoi_diem_chuan",
                    "response": {"type": "standard_score", "data": []}
                }
            ]
        }
    }


@pytest.fixture
def sample_entities():
    """Sample entities for testing"""
    return {
        "major_entities": [
            {"label": "TEN_NGANH", "text": "kiến trúc", "source": "pattern"},
            {"label": "MA_NGANH", "text": "7580101", "source": "pattern"},
            {"label": "CHUYEN_NGANH", "text": "công nghệ thông tin", "source": "dictionary"},
        ],
        "year_entities": [
            {"label": "NAM_HOC", "text": "2024", "source": "pattern"},
            {"label": "NAM_TUYEN_SINH", "text": "2025", "source": "pattern"},
        ],
        "method_entities": [
            {"label": "PHUONG_THUC", "text": "xét tuyển điểm thi THPT", "source": "pattern"},
        ],
        "mixed_entities": [
            {"label": "TEN_NGANH", "text": "kiến trúc", "source": "pattern"},
            {"label": "NAM_HOC", "text": "2024", "source": "pattern"},
        ]
    }


@pytest.fixture(scope="session")
def test_session_id():
    """Unique session ID for test isolation"""
    return "test_session_pytest"


@pytest.fixture(autouse=True)
def reset_test_context(nlp_service, test_session_id):
    """Auto reset context before each test"""
    nlp_service.reset_context(test_session_id)
    yield
    # Cleanup after test
    nlp_service.reset_context(test_session_id)
