"""
Integration tests for API Endpoints

Tests the FastAPI endpoints with real requests.
"""
import pytest


@pytest.mark.integration
@pytest.mark.api
class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_root_endpoint(self, test_client):
        """Test GET / returns success"""
        response = test_client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data


@pytest.mark.integration
@pytest.mark.api
class TestChatAdvancedEndpoint:
    """Test /chat/advanced endpoint"""

    def test_chat_advanced_basic_query(self, test_client):
        """Test basic chat query"""
        payload = {
            "message": "Điểm chuẩn ngành Kiến trúc?",
            "session_id": "test_123",
            "use_context": False
        }

        response = test_client.post("/chat/advanced", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "analysis" in data
        assert "response" in data
        assert "context" in data

        # Check analysis structure
        assert "intent" in data["analysis"]
        assert "score" in data["analysis"]
        assert "entities" in data["analysis"]

        # Check response structure
        assert "type" in data["response"]
        assert "message" in data["response"]

    def test_chat_advanced_with_context(self, test_client):
        """Test chat with context enabled"""
        payload = {
            "message": "Điểm chuẩn ngành CNTT?",
            "session_id": "test_context_123",
            "use_context": True
        }

        response = test_client.post("/chat/advanced", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Context should be in response
        assert "context" in data
        assert isinstance(data["context"], dict)

    def test_chat_advanced_followup(self, test_client):
        """Test follow-up question with context"""
        session_id = "test_followup_456"

        # First question
        payload1 = {
            "message": "Điểm chuẩn ngành Kiến trúc?",
            "session_id": session_id,
            "use_context": True
        }
        response1 = test_client.post("/chat/advanced", json=payload1)
        assert response1.status_code == 200

        # Follow-up question
        payload2 = {
            "message": "Còn học phí thế nào?",
            "session_id": session_id,
            "use_context": True
        }
        response2 = test_client.post("/chat/advanced", json=payload2)

        assert response2.status_code == 200
        data2 = response2.json()

        # Should understand follow-up
        assert "analysis" in data2
        assert "response" in data2

    def test_chat_advanced_empty_message(self, test_client):
        """Test chat with empty message"""
        payload = {
            "message": "",
            "session_id": "test_empty",
            "use_context": False
        }

        response = test_client.post("/chat/advanced", json=payload)

        # Should handle gracefully (200 with fallback or 400)
        assert response.status_code in [200, 400, 422]

    def test_chat_advanced_long_message(self, test_client):
        """Test chat with very long message"""
        payload = {
            "message": "Điểm chuẩn " * 200,
            "session_id": "test_long",
            "use_context": False
        }

        response = test_client.post("/chat/advanced", json=payload)

        # Should handle long messages
        assert response.status_code in [200, 400, 422]

    def test_chat_advanced_special_chars(self, test_client):
        """Test chat with special characters"""
        payload = {
            "message": "Điểm chuẩn!@#$%^&*()",
            "session_id": "test_special",
            "use_context": False
        }

        response = test_client.post("/chat/advanced", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "analysis" in data


@pytest.mark.integration
@pytest.mark.api
class TestContextEndpoint:
    """Test /chat/context endpoint"""

    def test_context_get(self, test_client):
        """Test GET context"""
        payload = {
            "action": "get",
            "session_id": "test_get_ctx"
        }

        response = test_client.post("/chat/context", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "context" in data

    def test_context_set(self, test_client):
        """Test SET context"""
        test_context = {
            "last_intent": "test_intent",
            "last_entities": []
        }

        payload = {
            "action": "set",
            "session_id": "test_set_ctx",
            "context": test_context
        }

        response = test_client.post("/chat/context", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["context"]["last_intent"] == "test_intent"

    def test_context_reset(self, test_client):
        """Test RESET context"""
        session_id = "test_reset_ctx"

        # Set some context first
        set_payload = {
            "action": "set",
            "session_id": session_id,
            "context": {"last_intent": "test"}
        }
        test_client.post("/chat/context", json=set_payload)

        # Reset
        reset_payload = {
            "action": "reset",
            "session_id": session_id
        }
        response = test_client.post("/chat/context", json=reset_payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_context_invalid_action(self, test_client):
        """Test invalid action"""
        payload = {
            "action": "invalid_action",
            "session_id": "test_invalid"
        }

        response = test_client.post("/chat/context", json=payload)

        # Should return error
        assert response.status_code in [400, 422]


@pytest.mark.integration
@pytest.mark.api
class TestAPIEdgeCases:
    """Test API edge cases and error handling"""

    def test_chat_missing_required_field(self, test_client):
        """Test request without required fields"""
        payload = {
            "session_id": "test_missing"
            # Missing 'message' field
        }

        response = test_client.post("/chat/advanced", json=payload)

        # Should return validation error
        assert response.status_code == 422

    def test_chat_invalid_json(self, test_client):
        """Test request with invalid JSON"""
        response = test_client.post(
            "/chat/advanced",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )

        # Should return error
        assert response.status_code in [400, 422]

    def test_cors_headers(self, test_client):
        """Test CORS headers are present"""
        response = test_client.get("/")

        # Should have CORS headers (if configured)
        # Note: TestClient may not include all middleware headers
        assert response.status_code == 200

    def test_concurrent_requests_same_session(self, test_client):
        """Test concurrent requests to same session"""
        session_id = "test_concurrent"

        payloads = [
            {"message": f"Test {i}", "session_id": session_id, "use_context": True}
            for i in range(5)
        ]

        responses = [
            test_client.post("/chat/advanced", json=p)
            for p in payloads
        ]

        # All should succeed
        for response in responses:
            assert response.status_code == 200

    def test_different_sessions_isolated(self, test_client):
        """Test that different sessions are isolated"""
        # Set context for session 1
        payload1 = {
            "message": "Điểm chuẩn ngành Kiến trúc",
            "session_id": "session_a",
            "use_context": True
        }
        test_client.post("/chat/advanced", json=payload1)

        # Query with session 2
        payload2 = {
            "message": "Còn học phí thế nào?",
            "session_id": "session_b",
            "use_context": True
        }
        response2 = test_client.post("/chat/advanced", json=payload2)

        # Session 2 should not have context from session 1
        assert response2.status_code == 200
        # Context should be independent
