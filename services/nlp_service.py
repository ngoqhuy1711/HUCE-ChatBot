"""NLP Service - Xử lý ngôn ngữ tự nhiên và quản lý context hội thoại."""

from typing import Dict, Any

from config import get_intent_threshold, get_context_history_limit
from nlu.pipeline import NLPPipeline


class ContextStore:
    """Lưu trữ context hội thoại trong RAM. Production nên dùng Redis."""

    def __init__(self) -> None:
        self._store: Dict[str, Dict[str, Any]] = {}

    def get(self, session_id: str) -> Dict[str, Any]:
        """Lấy context của session."""
        return self._store.get(session_id, {})

    def set(self, session_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Đặt context cho session."""
        self._store[session_id] = context
        return context

    def reset(self, session_id: str) -> None:
        """Xóa context của session."""
        if session_id in self._store:
            del self._store[session_id]

    def append_history(self, session_id: str, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Thêm entry vào lịch sử hội thoại (giới hạn 10 câu)."""
        ctx = self.get(session_id)
        hist = ctx.get("conversation_history", []) + [entry]

        limit = get_context_history_limit()
        if len(hist) > limit:
            hist = hist[-limit:]

        ctx["conversation_history"] = hist
        self.set(session_id, ctx)
        return ctx


class NLPService:
    """Service NLP tổng hợp - Điều phối xử lý ngôn ngữ, context và dữ liệu."""

    def __init__(self) -> None:
        """Khởi tạo NLP Service (chỉ gọi 1 lần khi app khởi động)."""
        self.pipeline = NLPPipeline()
        self.context_store = ContextStore()
        self.intent_threshold = get_intent_threshold()

    def analyze_message(self, message: str) -> Dict[str, Any]:
        """Phân tích NLP đơn giản - Chỉ trả intent + entities."""
        return self.pipeline.analyze(message)

    def handle_message(self, message: str, current_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Xử lý câu hỏi hoàn chỉnh: NLP + lấy dữ liệu + fallback.

        Flow: Analyze NLP → Check confidence → Get data hoặc Fallback
        """
        from services import csv_service as csvs

        analysis = self.pipeline.analyze(message)

        if analysis["intent"] == "fallback" or analysis["score"] < self.intent_threshold:
            response = csvs.handle_fallback_query(message, current_context)
            analysis["intent"] = "fallback_response"
        else:
            response = csvs.handle_intent_query(analysis, current_context, message)

        return {"analysis": analysis, "response": response}

    def get_context(self, session_id: str) -> Dict[str, Any]:
        """Lấy context của session."""
        return self.context_store.get(session_id)

    def set_context(self, session_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Lưu context cho session."""
        return self.context_store.set(session_id, context)

    def reset_context(self, session_id: str) -> None:
        """Xóa context (bắt đầu hội thoại mới)."""
        self.context_store.reset(session_id)

    def append_history(self, session_id: str, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Thêm entry vào lịch sử hội thoại."""
        return self.context_store.append_history(session_id, entry)


# Singleton instance
nlp_service = NLPService()


def get_nlp_service() -> NLPService:
    """Trả về singleton instance của NLPService."""
    return nlp_service
