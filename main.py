"""
FastAPI Backend cho Chatbot Tư vấn Tuyển sinh HUCE

==== KIẾN TRÚC TỔNG QUAN ====
File này chứa TẤT CẢ API endpoints của ứng dụng (đơn giản hóa từ việc tách router).

Cấu trúc:
┌─────────────────────────────────────────────┐
│  main.py (FastAPI App)                      │
│  ├── Health check (/)                       │
│  ├── Chat endpoints (/chat/advanced, /chat/context) │
└─────────────────────────────────────────────┘
         ↓ Gọi xuống
┌─────────────────────────────────────────────┐
│  Services Layer                             │
│  ├── nlp_service: NLP + Context             │
│  └── csv_service: Dữ liệu CSV (gọi gián tiếp) │
└─────────────────────────────────────────────┘
         ↓ Sử dụng
┌─────────────────────────────────────────────┐
│  NLU Layer                                  │
│  ├── pipeline: Điều phối NLP                │
│  ├── intent: Nhận diện ý định               │
│  ├── entities: Trích xuất thực thể          │
│  └── preprocess: Chuẩn hóa văn bản          │
└─────────────────────────────────────────────┘

==== CÁC API ENDPOINT ====

1. HEALTH CHECK
   GET  /  → Kiểm tra server hoạt động

2. CHAT (Hội thoại)
   POST /chat/advanced → Chat đầy đủ (NLP + dữ liệu + context + fallback)
   POST /chat/context  → Quản lý context (get/set/reset)
   

==== LUỒNG XỬ LÝ REQUEST ====
1. Client gửi request → FastAPI endpoint
2. Endpoint validate dữ liệu (Pydantic)
3. Endpoint gọi service (nlp_service hoặc csv_service)
4. Service xử lý logic và trả về dữ liệu
5. Endpoint trả response về client



LÝ DO:
- Dự án nhỏ (3 endpoints chính) → 1 file dễ quản lý hơn
- Debug nhanh hơn (không nhảy qua nhiều file)
- Đơn giản hơn cho 1 người maintain
- Vẫn rõ ràng với comment đầy đủ
"""

import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Import config và constants
from config import get_cors_origins, get_cors_allow_credentials, get_log_level
from constants import Validation, ErrorMessage, SuccessMessage
from models import (
    AdvancedChatRequest,
    ContextRequest,
    create_success_response,
)
# Import services
from services.nlp_service import get_nlp_service

# ============================================================================
# PHẦN 0: CẤU HÌNH LOGGING
# ============================================================================
# Logging giúp:
# 1. Debug khi có lỗi (xem log file để biết lỗi ở đâu)
# 2. Theo dõi user queries (phân tích câu hỏi thực tế để cải thiện NLP)
# 3. Monitor performance (xem API nào chậm)
# 4. Viết báo cáo (thống kê số lượng queries, intent phổ biến)

# Tạo thư mục logs nếu chưa có
log_dir = os.path.join(os.path.dirname(__file__), "logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Lấy log level từ environment
log_level_str = get_log_level()
log_level = getattr(logging, log_level_str, logging.INFO)

# Cấu hình logging với 2 handlers:
# 1. FileHandler: Ghi log vào file logs/chatbot.log (để xem sau)
# 2. StreamHandler: In log ra console (để debug realtime)
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        # Handler 1: Ghi vào file
        logging.FileHandler(os.path.join(log_dir, "chatbot.log"), encoding="utf-8"),
        # Handler 2: In ra console
        logging.StreamHandler(),
    ],
)

# Tạo logger cho module này
logger = logging.getLogger(__name__)

# ============================================================================
# PHẦN 1: KHỞI TẠO ỨNG DỤNG FASTAPI
# ============================================================================

app = FastAPI(
    title="HUCE Chatbot API",
    description="API cho Chatbot tư vấn tuyển sinh Đại học Xây dựng Hà Nội",
    version="1.0.0",
)

# ============================================================================
# PHẦN 1.5: CẤU HÌNH CORS (Cross-Origin Resource Sharing)
# ============================================================================
# CORS cho phép frontend (React/Vite/Reflex chạy ở port khác) gọi API backend
# Ví dụ: Frontend chạy ở http://localhost:3000, backend ở http://localhost:8000
# Nếu không config CORS → Browser sẽ block request (CORS policy error)

# Lấy CORS config từ environment
cors_origins = get_cors_origins()
cors_allow_credentials = get_cors_allow_credentials()

app.add_middleware(
    CORSMiddleware,
    # allow_origins: Danh sách domain được phép gọi API (từ environment hoặc mặc định)
    allow_origins=cors_origins,
    # allow_credentials: Cho phép gửi cookies/credentials
    allow_credentials=cors_allow_credentials,
    # allow_methods: Cho phép tất cả HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_methods=["*"],
    # allow_headers: Cho phép tất cả headers (Content-Type, Authorization, etc.)
    allow_headers=["*"],
)

# Log khi server khởi động
logger.info("=" * 60)
logger.info("HUCE Chatbot API Server đang khởi động...")
logger.info("=" * 60)
logger.info("CORS đã bật cho: %s", ", ".join(cors_origins))
logger.info("Swagger docs: http://localhost:8000/docs")
logger.info("=" * 60)

# Lấy NLP service singleton
# Service này chứa: pipeline (NLP), context_store (lưu context)
# Được khởi tạo MỘT LẦN khi app start, dùng chung cho mọi request
nlp = get_nlp_service()
logger.info("NLP Service đã khởi tạo thành công")


# ============================================================================
# PHẦN 2: ENDPOINTS - HEALTH CHECK
# ============================================================================


@app.get("/")
async def root():
    """
    Health check endpoint - Kiểm tra server hoạt động.

    Returns:
        {"success": true, "message": "HUCE Chatbot API đang hoạt động"}

    Usage:
        curl http://localhost:8000/
    """
    return create_success_response(message="HUCE Chatbot API đang hoạt động")


# ============================================================================
# PHẦN 3: ENDPOINTS - CHAT (Hội thoại)
# ============================================================================


@app.post("/chat/context")
async def manage_chat_context(req: ContextRequest):
    """
    Quản lý context hội thoại - get/set/reset.

    Context giúp bot "nhớ" cuộc trò chuyện để xử lý câu hỏi tiếp theo.

    Các action:
    - "get": Lấy context hiện tại
    - "set": Đặt context mới
    - "reset": Xóa context (bắt đầu hội thoại mới)

    Args:
        req: ContextRequest chứa:
            - action: "get" | "set" | "reset"
            - session_id: ID phiên (mặc định "default")
            - context: Context mới (chỉ khi action="set")

    Returns:
        - GET: {"success": true, "context": {...}}
        - SET: {"success": true, "message": "...", "context": {...}}
        - RESET: {"success": true, "message": "..."}

    Example 1 - Get context:
        POST /chat/context
        {"action": "get", "session_id": "user_123"}

    Example 2 - Reset context:
        POST /chat/context
        {"action": "reset", "session_id": "user_123"}
    """
    try:
        action = req.action
        session_id = req.session_id or "default"

        if action == Validation.ACTION_GET:
            # Lấy context của session
            context = nlp.get_context(session_id)
            logger.info(
                f"Endpoint /chat/context - Lấy context cho session: {session_id}"
            )
            return create_success_response() | {"context": context}

        elif action == Validation.ACTION_SET:
            # Đặt context mới
            context = req.context or {}
            nlp.set_context(session_id, context)
            logger.info(
                f"Endpoint /chat/context - Cập nhật context cho session: {session_id}"
            )
            return create_success_response(message=SuccessMessage.CONTEXT_UPDATED) | {
                "context": context
            }

        elif action == Validation.ACTION_RESET:
            # Xóa context (bắt đầu hội thoại mới)
            nlp.reset_context(session_id)
            logger.info(
                f"Endpoint /chat/context - Reset context cho session: {session_id}"
            )
            return create_success_response(message=SuccessMessage.CONTEXT_RESET)

        else:
            # Action không hợp lệ (không nên xảy ra vì đã validate trong model)
            raise ValueError(ErrorMessage.INVALID_ACTION)

    except ValueError as e:
        logger.warning(f"Lỗi validation tại /chat/context: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Lỗi hệ thống tại /chat/context: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=ErrorMessage.INTERNAL_ERROR)


@app.post("/chat/advanced")
async def advanced_chat(req: AdvancedChatRequest):
    """
    Chat nâng cao - ĐẦY ĐỦ tính năng (NLP + dữ liệu + context + fallback).

    Đây là endpoint chính cho chatbot production, bao gồm:
    - Phân tích NLP (intent + entities)
    - Lấy dữ liệu từ CSV theo intent
    - Sử dụng context để hiểu câu hỏi tiếp theo
    - Fallback thông minh khi không hiểu
    - Tự động cập nhật context sau mỗi câu

    Luồng xử lý:
    ┌──────────────────────────────────────────┐
    │ 1. Lấy context hiện tại (nếu use_context)│
    └──────────────────────────────────────────┘
                    ↓
    ┌──────────────────────────────────────────┐
    │ 2. Phân tích NLP + lấy dữ liệu           │
    │    - Intent rõ → Lấy từ CSV              │
    │    - Intent không rõ → Fallback          │
    └──────────────────────────────────────────┘
                    ↓
    ┌──────────────────────────────────────────┐
    │ 3. Cập nhật context với câu hỏi mới      │
    │    - Thêm vào lịch sử                    │
    │    - Lưu last_intent, last_entities      │
    └──────────────────────────────────────────┘
                    ↓
    ┌──────────────────────────────────────────┐
    │ 4. Trả về response + context mới         │
    └──────────────────────────────────────────┘

    Args:
        req: AdvancedChatRequest chứa:
            - message: Câu hỏi
            - session_id: ID phiên
            - use_context: Có dùng context không

    Returns:
        {
            "analysis": {
                "intent": str,
                "score": float,
                "entities": list
            },
            "response": {
                "type": str,
                "data": list,
                "message": str
            },
            "context": {
                "last_intent": str,
                "last_entities": list,
                "conversation_history": list
            }
        }

    Example Conversation:
        User 1: "Điểm chuẩn ngành Kiến trúc"
        → Intent rõ → Trả điểm chuẩn từ CSV
        → Lưu context: last_intent="hoi_diem_chuan", last_entities=[Kiến trúc]

        User 2: "Còn điểm sàn?"
        → Dùng context → Biết "còn" = tiếp tục hỏi về Kiến trúc
        → Trả điểm sàn Kiến trúc
    """
    try:
        # Log request với session_id để tracking user
        logger.info(
            f"💬 /chat/advanced - Session: {req.session_id} - Message: {req.message[:100]}"
        )

        message = req.message
        session_id = req.session_id or "default"
        use_context = req.use_context if req.use_context is not None else True

        # Bước 1: Lấy context hiện tại (nếu dùng context)
        current_context = nlp.get_context(session_id) if use_context else {}

        # Bước 2: Xử lý message (NLP + dữ liệu + fallback)
        result = nlp.handle_message(message, current_context)
        analysis = result["analysis"]
        response = result["response"]

        # Log kết quả phân tích
        logger.info(
            f"✅ /chat/advanced - Intent: {analysis['intent']} "
            f"(score: {analysis['score']:.2f}) - "
            f"Response type: {response.get('type', 'unknown')}"
        )

        # Bước 3: Cập nhật context
        # Thêm câu hỏi-trả lời vào lịch sử
        new_context = nlp.append_history(
            session_id,
            {"message": message, "intent": analysis["intent"], "response": response},
        )
        # Lưu intent và entities của câu hiện tại
        new_context["last_intent"] = analysis["intent"]
        new_context["last_entities"] = analysis["entities"]

        # Bước 4: Trả về kết quả đầy đủ
        return {"analysis": analysis, "response": response, "context": new_context}

    except Exception as e:
        # Log lỗi chi tiết để debug
        logger.error(
            f"❌ Error in /chat/advanced - Session: {req.session_id} - "
            f"Message: {req.message[:100]} - Error: {str(e)}",
            exc_info=True,
        )
        # Trả về lỗi 500 với fallback response thân thiện
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Xin lỗi, có lỗi xảy ra khi xử lý câu hỏi của bạn. Vui lòng thử lại.",
                "debug_info": str(e) if logger.level == logging.DEBUG else None,
            },
        )


# ============================================================================
# CHẠY ỨNG DỤNG
# ============================================================================
# Nếu chạy trực tiếp file này: python main.py
# (Thường không dùng, nên dùng uvicorn)
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
