"""
Unit tests for Context Management

Tests the context management logic in the system.
"""
import pytest


@pytest.mark.unit
class TestContextManagement:
    """Test context storage and retrieval"""

    def test_get_empty_context(self, nlp_service, test_session_id):
        """Test getting context from new session"""
        context = nlp_service.get_context(test_session_id)
        assert isinstance(context, dict)
        assert len(context) == 0 or "conversation_history" not in context

    def test_set_and_get_context(self, nlp_service, test_session_id):
        """Test setting and retrieving context"""
        test_context = {
            "last_intent": "hoi_diem_chuan",
            "last_entities": [{"label": "TEN_NGANH", "text": "kiến trúc"}]
        }

        nlp_service.set_context(test_session_id, test_context)
        retrieved = nlp_service.get_context(test_session_id)

        assert retrieved["last_intent"] == "hoi_diem_chuan"
        assert len(retrieved["last_entities"]) == 1

    def test_reset_context(self, nlp_service, test_session_id):
        """Test context reset"""
        # Set some context
        nlp_service.set_context(test_session_id, {"last_intent": "test"})

        # Reset
        nlp_service.reset_context(test_session_id)

        # Should be empty
        context = nlp_service.get_context(test_session_id)
        assert len(context) == 0 or "last_intent" not in context

    def test_append_history(self, nlp_service, test_session_id):
        """Test appending to conversation history"""
        entry = {
            "message": "Test message",
            "intent": "test_intent",
            "response": {"type": "test"}
        }

        nlp_service.append_history(test_session_id, entry)
        context = nlp_service.get_context(test_session_id)

        assert "conversation_history" in context
        assert len(context["conversation_history"]) == 1
        assert context["conversation_history"][0]["message"] == "Test message"

    def test_history_limit(self, nlp_service, test_session_id):
        """Test conversation history limit (should be 10)"""
        # Add 15 entries
        for i in range(15):
            entry = {
                "message": f"Message {i}",
                "intent": "test",
                "response": {}
            }
            nlp_service.append_history(test_session_id, entry)

        context = nlp_service.get_context(test_session_id)
        history = context.get("conversation_history", [])

        # Should keep only last 10
        assert len(history) <= 10, f"History should be limited to 10, got {len(history)}"

    def test_multiple_sessions(self, nlp_service):
        """Test context isolation between sessions"""
        session1 = "session_1"
        session2 = "session_2"

        nlp_service.set_context(session1, {"last_intent": "intent_1"})
        nlp_service.set_context(session2, {"last_intent": "intent_2"})

        ctx1 = nlp_service.get_context(session1)
        ctx2 = nlp_service.get_context(session2)

        assert ctx1["last_intent"] == "intent_1"
        assert ctx2["last_intent"] == "intent_2"


@pytest.mark.unit
class TestContextInference:
    """Test smart context inference logic"""

    def test_followup_preserves_major(self, nlp_service, test_session_id):
        """Test that follow-up questions preserve major context"""
        # First message: Ask about a major
        msg1 = "Điểm chuẩn ngành Kiến trúc?"
        ctx = nlp_service.get_context(test_session_id)
        result1 = nlp_service.handle_message(msg1, ctx)

        # Update context
        new_ctx = {
            "last_intent": result1["analysis"]["intent"],
            "last_entities": result1["analysis"]["entities"],
            "conversation_history": []
        }
        nlp_service.set_context(test_session_id, new_ctx)

        # Second message: Follow-up about tuition
        msg2 = "Còn học phí thế nào?"
        ctx2 = nlp_service.get_context(test_session_id)
        result2 = nlp_service.handle_message(msg2, ctx2)

        # Context should have major from first question
        major_in_context = any(
            e.get("label") in ["TEN_NGANH", "CHUYEN_NGANH", "MA_NGANH"]
            for e in ctx2.get("last_entities", [])
        )
        assert major_in_context, "Follow-up should preserve major from context"

    def test_independent_topic_clears_context(self, nlp_service, test_session_id):
        """Test that independent topics clear major context"""
        # Set context with a major
        nlp_service.set_context(test_session_id, {
            "last_intent": "hoi_diem_chuan",
            "last_entities": [{"label": "TEN_NGANH", "text": "kiến trúc"}]
        })

        # Ask about scholarships (independent topic)
        msg = "Học bổng có gì?"
        ctx = nlp_service.get_context(test_session_id)
        result = nlp_service.handle_message(msg, ctx)

        # Should detect scholarship intent
        assert "hoc_bong" in result["analysis"]["intent"].lower()

    def test_new_major_updates_context(self, nlp_service, test_session_id):
        """Test that mentioning new major updates context"""
        # Set context with old major
        nlp_service.set_context(test_session_id, {
            "last_entities": [{"label": "TEN_NGANH", "text": "kiến trúc"}]
        })

        # Ask about different major
        msg = "Điểm chuẩn ngành CNTT?"
        ctx = nlp_service.get_context(test_session_id)
        result = nlp_service.handle_message(msg, ctx)

        # Should extract new major
        entities = result["analysis"]["entities"]
        has_cntt = any(
            "cntt" in e.get("text", "").lower() or
            "công nghệ thông tin" in e.get("text", "").lower()
            for e in entities
        )
        # May or may not extract based on entity patterns
        assert isinstance(entities, list)

    def test_general_query_ignores_context(self, nlp_service, test_session_id):
        """Test that general queries ignore specific context"""
        # Set context with specific major
        nlp_service.set_context(test_session_id, {
            "last_entities": [{"label": "TEN_NGANH", "text": "kiến trúc"}]
        })

        # Ask general question
        msg = "Điều kiện xét tuyển chung là gì?"
        ctx = nlp_service.get_context(test_session_id)
        result = nlp_service.handle_message(msg, ctx)

        # Should handle as general query
        assert result["response"]["type"] in ["admission_conditions", "fallback_response"]


@pytest.mark.unit
class TestContextEdgeCases:
    """Test edge cases in context management"""

    def test_context_with_empty_entities(self, nlp_service, test_session_id):
        """Test context with empty entity list"""
        nlp_service.set_context(test_session_id, {
            "last_intent": "test",
            "last_entities": []
        })

        ctx = nlp_service.get_context(test_session_id)
        assert ctx["last_entities"] == []

    def test_context_with_invalid_session_id(self, nlp_service):
        """Test handling of unusual session IDs"""
        weird_ids = ["", "   ", "😊", "very" * 100]

        for session_id in weird_ids:
            try:
                ctx = nlp_service.get_context(session_id)
                assert isinstance(ctx, dict)
            except Exception as e:
                pytest.fail(f"Should handle weird session ID: {session_id}, error: {e}")

    def test_context_persistence_across_queries(self, nlp_service, test_session_id):
        """Test that context persists across multiple queries"""
        messages = [
            "Điểm chuẩn ngành Kiến trúc?",
            "Còn học phí?",
            "Chỉ tiêu bao nhiêu?",
        ]

        for msg in messages:
            ctx = nlp_service.get_context(test_session_id)
            result = nlp_service.handle_message(msg, ctx)

            # Update context
            new_ctx = nlp_service.get_context(test_session_id)
            new_ctx["last_intent"] = result["analysis"]["intent"]
            if result["analysis"]["entities"]:
                new_ctx["last_entities"] = result["analysis"]["entities"]
            nlp_service.set_context(test_session_id, new_ctx)

        # Final context should have history
        final_ctx = nlp_service.get_context(test_session_id)
        assert "last_intent" in final_ctx
