"""
Dịch vụ NLP tổng hợp - Quản lý toàn bộ logic xử lý ngôn ngữ tự nhiên và context.

==== TÓM TẮT ====
File này gộp 3 services cũ thành 1:
1. ContextStore (lưu context hội thoại)
2. ConversationService (điều phối chat)
3. AppState (singleton container)

→ ĐƠN GIẢN HƠN: 1 file thay vì 3 files, nhưng vẫn rõ ràng.

==== CẤU TRÚC ====
┌─────────────────────────────────────────────────────┐
│  NLPService (Singleton)                             │
│  ├── pipeline: NLPPipeline (intent + entity)        │
│  ├── context_store: ContextStore (lưu context)      │
│  ├── intent_threshold: float (ngưỡng confidence)    │
│  │                                                  │
│  ├── analyze_message()   → Chỉ NLP                  │
│  ├── handle_message()    → NLP + dữ liệu + fallback │
│  ├── get_context()       → Lấy context              │
│  ├── set_context()       → Lưu context              │
│  ├── reset_context()     → Xóa context              │
│  └── append_history()    → Thêm vào lịch sử         │
└─────────────────────────────────────────────────────┘

==== LUỒNG XỬ LÝ CHAT ====
1. User gửi message → API endpoint
2. API gọi nlp_service.handle_message(message, context)
3. NLPService:
   a. Phân tích NLP (intent + entities)
   b. Kiểm tra confidence score
   c. Nếu score cao → Lấy dữ liệu từ CSV theo intent
   d. Nếu score thấp → Fallback (tìm theo từ khóa)
4. Trả response về API → User

==== CONTEXT LÀ GÌ? ====
Context = ngữ cảnh hội thoại, giúp bot "nhớ" cuộc trò chuyện.

Ví dụ:
  User: "Điểm chuẩn ngành Kiến trúc?"
  Bot: "25.5 điểm"
  User: "Còn điểm sàn?"  ← Bot biết "còn" = tiếp tục hỏi về Kiến trúc

Context lưu:
- last_intent: "hoi_diem_chuan"
- last_entities: [{"label": "TEN_NGANH", "text": "kiến trúc"}]
- conversation_history: 10 câu hỏi-trả lời gần nhất

==== CƠ CHẾ FALLBACK ====
Khi NLP không nhận diện được intent (score < 0.35):
- KHÔNG trả "Tôi không hiểu"
- Tìm kiếm theo từ khóa đơn giản
- Gợi ý cách hỏi rõ hơn

==== TẠI SAO GỘP 3 FILES? ====
TRƯỚC (3 files riêng):
- app_state.py: Chỉ tạo singleton
- context_store.py: Chỉ lưu/lấy context
- conversation_service.py: Điều phối chat
→ Quá phân mảnh, nhảy qua lại nhiều file

SAU (1 file gộp):
- Tất cả logic NLP ở 1 nơi
- Dễ đọc, dễ maintain
- Vẫn rõ ràng với comment đầy đủ
"""

from typing import Dict, Any
from config import get_intent_threshold, get_context_history_limit
from nlu.pipeline import NLPPipeline


class ContextStore:
    """
    Lưu trữ context hội thoại trong bộ nhớ RAM (in-memory).
    
    ==== CẤU TRÚC DỮ LIỆU ====
    _store = {
        "session_id_1": {
            "last_intent": "hoi_diem_chuan",
            "last_entities": [{"label": "TEN_NGANH", "text": "kiến trúc"}],
            "conversation_history": [
                {"message": "...", "intent": "...", "response": {...}},
                ...  # Tối đa 10 câu
            ]
        },
        "session_id_2": {...}
    }
    
    ==== LƯU Ý ====
    - In-memory: Mất khi restart server
    - Production: Nên dùng Redis (persistent, scalable)
    - Giới hạn 10 câu/session để tiết kiệm bộ nhớ
    """
    
    def __init__(self) -> None:
        """Khởi tạo dict rỗng để lưu context."""
        self._store: Dict[str, Dict[str, Any]] = {}
    
    def get(self, session_id: str) -> Dict[str, Any]:
        """
        Lấy context của một session.
        
        Args:
            session_id: ID phiên hội thoại (vd: "user_abc_123")
            
        Returns:
            Context của session, hoặc {} nếu chưa có
        """
        return self._store.get(session_id, {})
    
    def set(self, session_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Đặt/cập nhật context cho một session.
        
        Args:
            session_id: ID phiên
            context: Context mới (ghi đè hoàn toàn)
            
        Returns:
            Context vừa được lưu
        """
        self._store[session_id] = context
        return context
    
    def reset(self, session_id: str) -> None:
        """
        Xóa context của một session (bắt đầu hội thoại mới).
        
        Args:
            session_id: ID phiên cần xóa
        """
        if session_id in self._store:
            del self._store[session_id]
    
    def append_history(self, session_id: str, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Thêm một entry vào lịch sử hội thoại.
        
        Luồng xử lý:
        1. Lấy context hiện tại
        2. Lấy conversation_history (list các câu hỏi-trả lời)
        3. Thêm entry mới vào cuối
        4. Nếu list > 10 câu: Chỉ giữ 10 câu gần nhất
        5. Cập nhật lại context
        
        Args:
            session_id: ID phiên
            entry: Entry mới chứa:
                {
                    "message": "Câu hỏi user",
                    "intent": "Intent nhận diện",
                    "response": {...}  # Response từ bot
                }
                
        Returns:
            Context đã cập nhật
        """
        # Lấy context hiện tại
        ctx = self.get(session_id)
        
        # Lấy lịch sử và thêm entry mới
        hist = ctx.get("conversation_history", []) + [entry]
        
        # Giới hạn độ dài (mặc định 10 câu)
        limit = get_context_history_limit()
        if len(hist) > limit:
            hist = hist[-limit:]  # Chỉ giữ 10 câu cuối
        
        # Cập nhật và lưu
        ctx["conversation_history"] = hist
        self.set(session_id, ctx)
        return ctx


class NLPService:
    """
    Service NLP tổng hợp - Điều phối toàn bộ logic xử lý ngôn ngữ.
    
    ==== CHỨC NĂNG CHÍNH ====
    1. Phân tích NLP (intent + entities)
    2. Xử lý fallback khi confidence thấp
    3. Quản lý context hội thoại
    4. Kết nối NLP với dữ liệu CSV
    
    ==== ATTRIBUTES ====
    - pipeline: NLPPipeline - Xử lý NLP core
    - context_store: ContextStore - Lưu trữ context
    - intent_threshold: float - Ngưỡng confidence (0.35)
    
    ==== METHODS ====
    - analyze_message(): Chỉ phân tích NLP (không lấy dữ liệu)
    - handle_message(): Xử lý đầy đủ (NLP + dữ liệu + fallback)
    - get_context(): Lấy context của session
    - set_context(): Lưu context
    - reset_context(): Xóa context (bắt đầu hội thoại mới)
    - append_history(): Thêm vào lịch sử hội thoại
    """
    
    def __init__(self) -> None:
        """
        Khởi tạo NLP Service.
        
        CẢNH BÁO: Hàm này chỉ gọi MỘT LẦN khi app khởi động!
        Không tạo NLPService() nhiều lần (tốn bộ nhớ).
        """
        # Pipeline NLP trung tâm
        # Load dữ liệu từ: intent.csv, entity.json, synonym.csv
        self.pipeline = NLPPipeline()
        
        # Kho lưu context hội thoại
        self.context_store = ContextStore()
        
        # Ngưỡng confidence (từ config.py)
        # Nếu score < threshold → Fallback
        self.intent_threshold = get_intent_threshold()
    
    def analyze_message(self, message: str) -> Dict[str, Any]:
        """
        Phân tích NLP đơn giản - CHỈ trả intent + entities.
        
        Dùng cho endpoint /chat (phân tích thô, không xử lý dữ liệu).
        
        Luồng xử lý:
        1. Chuẩn hóa văn bản (lowercase, loại ký tự đặc biệt)
        2. Tách từ bằng Underthesea
        3. Map từ đồng nghĩa (synonym.csv)
        4. Nhận diện intent (TF-IDF + cosine similarity)
        5. Trích xuất entities (pattern + dictionary + NER)
        
        Args:
            message: Câu hỏi từ người dùng
            
        Returns:
            {
                "intent": str,      # Ý định (vd: "hoi_diem_chuan")
                "score": float,     # Độ tin cậy 0-1
                "entities": list    # Entities trích xuất
            }
            
        Ví dụ:
            Input: "Điểm chuẩn ngành Kiến trúc"
            Output: {
                "intent": "hoi_diem_chuan",
                "score": 0.82,
                "entities": [{"label": "TEN_NGANH", "text": "kiến trúc"}]
            }
        """
        return self.pipeline.analyze(message)
    
    def handle_message(self, message: str, current_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Xử lý câu hỏi HOÀN CHỈNH: NLP + lấy dữ liệu + fallback.
        
        Dùng cho endpoint /chat/advanced (chatbot đầy đủ).
        
        Luồng xử lý:
        ┌──────────────────────────────────────────┐
        │ 1. Phân tích NLP (intent + entities)     │
        └──────────────────────────────────────────┘
                        ↓
        ┌──────────────────────────────────────────┐
        │ 2. Kiểm tra confidence score             │
        │    - score >= 0.35 → Intent rõ ràng      │
        │    - score < 0.35  → Intent không rõ     │
        └──────────────────────────────────────────┘
                        ↓
              ┌─────────┴─────────┐
              ↓                   ↓
        [Score cao]         [Score thấp]
              ↓                   ↓
        handle_intent_query  handle_fallback_query
        (Lấy từ CSV)         (Tìm theo keyword)
              ↓                   ↓
              └─────────┬─────────┘
                        ↓
        ┌──────────────────────────────────────────┐
        │ 3. Trả về analysis + response            │
        └──────────────────────────────────────────┘
        
        Args:
            message: Câu hỏi từ người dùng
            current_context: Context hiện tại của session (có thể rỗng)
                Chứa: last_intent, last_entities, conversation_history
                
        Returns:
            {
                "analysis": {
                    "intent": str,
                    "score": float,
                    "entities": list
                },
                "response": {
                    "type": str,        # Loại response
                    "data": list,       # Dữ liệu thực tế
                    "message": str      # Thông điệp cho user
                }
            }
            
        Ví dụ 1 - Intent rõ ràng:
            Input: "Điểm chuẩn ngành Kiến trúc 2025"
            Analysis: {"intent": "hoi_diem_chuan", "score": 0.85}
            → Lấy điểm chuẩn từ CSV
            
        Ví dụ 2 - Intent không rõ (fallback):
            Input: "điểm kiến trúc"
            Analysis: {"intent": "fallback", "score": 0.1}
            → Tìm theo từ khóa "điểm"
        """
        # Import csv_service ở đây để tránh circular import
        from services import csv_service as csvs
        
        # Bước 1: Phân tích NLP
        analysis = self.pipeline.analyze(message)
        
        # Bước 2: Kiểm tra confidence và xử lý
        if analysis["intent"] == "fallback" or analysis["score"] < self.intent_threshold:
            # Intent không rõ → Dùng fallback
            response = csvs.handle_fallback_query(message, current_context)
            # Đánh dấu đây là fallback response
            analysis["intent"] = "fallback_response"
        else:
            # Intent rõ ràng → Xử lý theo intent
            response = csvs.handle_intent_query(analysis, current_context)
        
        # Bước 3: Trả về kết quả đầy đủ
        return {
            "analysis": analysis,
            "response": response
        }
    
    # ========================================================================
    # CONTEXT MANAGEMENT - Các phương thức quản lý context
    # ========================================================================
    
    def get_context(self, session_id: str) -> Dict[str, Any]:
        """
        Lấy context của một session.
        
        Args:
            session_id: ID phiên hội thoại
            
        Returns:
            Context dict hoặc {} nếu chưa có
        """
        return self.context_store.get(session_id)
    
    def set_context(self, session_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Lưu context cho một session.
        
        Args:
            session_id: ID phiên
            context: Context mới
            
        Returns:
            Context vừa lưu
        """
        return self.context_store.set(session_id, context)
    
    def reset_context(self, session_id: str) -> None:
        """
        Xóa context (bắt đầu hội thoại mới).
        
        Args:
            session_id: ID phiên cần xóa
        """
        self.context_store.reset(session_id)
    
    def append_history(self, session_id: str, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Thêm một entry vào lịch sử hội thoại.
        
        Args:
            session_id: ID phiên
            entry: Entry mới (message, intent, response)
            
        Returns:
            Context đã cập nhật
        """
        return self.context_store.append_history(session_id, entry)


# ============================================================================
# SINGLETON INSTANCE - Tạo một lần duy nhất khi app khởi động
# ============================================================================
# Biến này được khởi tạo ngay khi module được import lần đầu
# Mọi lần sau đó đều dùng chung instance này (tiết kiệm bộ nhớ)
nlp_service = NLPService()


def get_nlp_service() -> NLPService:
    """
    Trả về singleton instance của NLPService.
    
    Đây là cách DUY NHẤT nên dùng để lấy service trong code.
    KHÔNG tự tạo NLPService() mới!
    
    Returns:
        NLPService: Instance duy nhất
        
    Example:
        ```python
        from services.nlp_service import get_nlp_service
        
        nlp = get_nlp_service()
        analysis = nlp.analyze_message("Điểm chuẩn ngành Kiến trúc")
        ```
    """
    return nlp_service

