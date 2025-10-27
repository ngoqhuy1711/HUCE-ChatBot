"""
FastAPI Backend cho Chatbot Tư vấn Tuyển sinh HUCE

==== KIẾN TRÚC TỔNG QUAN ====
File này chứa TẤT CẢ API endpoints của ứng dụng (đơn giản hóa từ việc tách router).

Cấu trúc:
┌─────────────────────────────────────────────┐
│  main.py (FastAPI App)                      │
│  ├── Health check (/)                       │
│  ├── Chat endpoints (/chat, /chat/advanced) │
│  ├── Data endpoints (/nganh, /diem, ...)    │
│  └── Helper endpoints (/goiy)               │
└─────────────────────────────────────────────┘
         ↓ Gọi xuống
┌─────────────────────────────────────────────┐
│  Services Layer                             │
│  ├── nlp_service: NLP + Context             │
│  └── csv_service: Dữ liệu CSV               │
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
   POST /chat          → Phân tích NLP đơn giản (intent + entities)
   POST /chat/advanced → Chat đầy đủ (NLP + dữ liệu + context + fallback)
   POST /chat/context  → Quản lý context (get/set/reset)

3. DATA (Tra cứu dữ liệu)
   GET  /nganh      → Danh sách ngành học
   GET  /diem       → Điểm chuẩn/điểm sàn
   GET  /hocphi     → Học phí
   GET  /hocbong    → Học bổng
   GET  /chi-tieu   → Chỉ tiêu tuyển sinh
   GET  /lich       → Lịch tuyển sinh
   GET  /kenh-nop   → Kênh nộp hồ sơ
   GET  /dieu-kien  → Điều kiện xét tuyển

4. HELPER (Hỗ trợ)
   POST /goiy → Gợi ý ngành theo điểm số

==== LUỒNG XỬ LÝ REQUEST ====
1. Client gửi request → FastAPI endpoint
2. Endpoint validate dữ liệu (Pydantic)
3. Endpoint gọi service (nlp_service hoặc csv_service)
4. Service xử lý logic và trả về dữ liệu
5. Endpoint trả response về client

==== CÁCH CHẠY ====
Từ thư mục gốc dự án:
    uvicorn backend.main:app --reload

Hoặc từ trong thư mục backend:
    uvicorn main:app --reload

==== TẠI SAO GỘP TẤT CẢ VÀO 1 FILE? ====
TRƯỚC: Tách 5 router files riêng (chat, majors, scores, tuition, scholarships)
SAU: Gộp tất cả vào main.py

LÝ DO:
- Dự án nhỏ (13 endpoints) → 1 file dễ quản lý hơn
- Debug nhanh hơn (không nhảy qua nhiều file)
- Đơn giản hơn cho 1 người maintain
- Vẫn rõ ràng với comment đầy đủ
"""

import logging
import os
from typing import Optional, Dict, Any
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Import services
from services.nlp_service import get_nlp_service
from services import csv_service as csvs

# Import config và constants
from config import DATA_DIR, get_cors_origins, get_cors_allow_credentials, get_log_level
from constants import Intent, ResponseType, Validation, ErrorMessage, SuccessMessage
from models import (
    ChatRequest,
    AdvancedChatRequest,
    ContextRequest,
    SuggestMajorsRequest,
    create_success_response,
    create_error_response,
)


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
logger.info("Thư mục dữ liệu: %s", DATA_DIR)
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


@app.post("/chat")
async def chat(req: ChatRequest):
    """
    Phân tích NLP đơn giản - CHỈ trả intent + entities.

    Endpoint này dùng cho:
    - Kiểm tra NLP có hoạt động không
    - Debug xem intent detection có chính xác không
    - Không lấy dữ liệu từ CSV, không xử lý context

    Luồng xử lý:
    1. Nhận message từ client
    2. Phân tích NLP (intent + entities)
    3. Trả về kết quả phân tích thô

    Args:
        req: ChatRequest chứa message

    Returns:
        {
            "success": true,
            "intent": str,      # Ý định nhận diện
            "confidence": float, # Độ tin cậy 0-1
            "entities": list    # Entities trích xuất
        }

    Example Request:
        POST /chat
        {"message": "Điểm chuẩn ngành Kiến trúc 2025"}

    Example Response:
        {
            "success": true,
            "intent": "hoi_diem_chuan",
            "confidence": 0.85,
            "entities": [
                {"label": "TEN_NGANH", "text": "kiến trúc"},
                {"label": "NAM_HOC", "text": "2025"}
            ]
        }
    """
    try:
        # Log request để theo dõi
        logger.info(f"Endpoint /chat - Tin nhắn: {req.message[:100]}")

        # Phân tích NLP
        analysis = nlp.analyze_message(req.message)

        # Log kết quả
        logger.info(
            f"Endpoint /chat - Intent: {analysis['intent']} (độ tin cậy: {analysis['score']:.2f})"
        )

        # Trả về với format chuẩn
        return {
            "success": True,
            "intent": analysis["intent"],
            "confidence": analysis["score"],
            "entities": analysis["entities"],
        }

    except ValueError as e:
        # Lỗi validation
        logger.warning(f"Lỗi validation tại /chat: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Lỗi hệ thống
        logger.error(f"Lỗi hệ thống tại /chat: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=ErrorMessage.INTERNAL_ERROR)


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
# PHẦN 5: ENDPOINTS - DATA (Tra cứu dữ liệu)
# ============================================================================


@app.get("/nganh")
async def get_majors(
    q: Optional[str] = Query(None, description="Tên hoặc mã ngành để tìm kiếm")
):
    """
    Tra cứu danh sách ngành học.

    Tham số:
    - q: Từ khóa tìm kiếm (tên ngành hoặc mã ngành), optional
         Nếu không truyền → Trả toàn bộ ngành

    Returns:
        {
            "items": [
                {
                    "ma_nganh": str,
                    "ten_nganh": str,
                    "khoi_thi": str,
                    "to_hop_mon": str,
                    "mo_ta": str
                },
                ...
            ]
        }

    Example 1 - Lấy tất cả ngành:
        GET /nganh

    Example 2 - Tìm kiếm:
        GET /nganh?q=kiến trúc
        → Trả các ngành có chữ "kiến trúc" trong tên

        GET /nganh?q=D510101
        → Trả ngành có mã D510101
    """
    items = csvs.list_majors(q)
    return {"items": items}


@app.get("/diem")
async def get_scores(
    score_type: str = Query(
        "chuan", description="Loại điểm: 'chuan' (điểm chuẩn) hoặc 'san' (điểm sàn)"
    ),
    major: Optional[str] = Query(None, description="Tên hoặc mã ngành"),
    year: Optional[str] = Query(None, description="Năm học, ví dụ: 2025"),
):
    """
    Tra cứu điểm chuẩn hoặc điểm sàn.

    Tham số:
    - score_type: "chuan" (mặc định) hoặc "san"
    - major: Tên/mã ngành (optional)
    - year: Năm học (optional)

    Returns:
        {
            "items": [
                {
                    "ma_nganh": str,
                    "ten_nganh": str,
                    "nam_hoc": str,
                    "diem_chuan" | "diem_san": float,
                    "khoi_thi": str
                },
                ...
            ]
        }

    Example 1 - Điểm chuẩn tất cả ngành năm 2025:
        GET /diem?score_type=chuan&year=2025

    Example 2 - Điểm sàn ngành Kiến trúc:
        GET /diem?score_type=san&major=kiến trúc

    Example 3 - Điểm chuẩn ngành Kiến trúc năm 2025:
        GET /diem?score_type=chuan&major=kiến trúc&year=2025
    """
    if score_type == "san":
        # Lấy điểm sàn
        items = csvs.find_floor_score(major, year)
    else:
        # Lấy điểm chuẩn (mặc định)
        items = csvs.find_standard_score(major, year)

    return {"items": items}


@app.get("/hocphi")
async def get_tuition(
    year: Optional[str] = Query(None, description="Năm học"),
    program: Optional[str] = Query(None, description="Chương trình đào tạo"),
):
    """
    Tra cứu học phí.

    Tham số:
    - year: Năm học (optional)
    - program: Chương trình đào tạo (optional)

    Returns:
        {
            "items": [
                {
                    "nam_hoc": str,
                    "chuong_trinh": str,
                    "hoc_phi": str,
                    "don_vi": str
                },
                ...
            ]
        }

    Example 1 - Học phí năm 2025:
        GET /hocphi?year=2025

    Example 2 - Học phí chương trình Đại học:
        GET /hocphi?program=đại học

    Example 3 - Tất cả học phí:
        GET /hocphi
    """
    items = csvs.list_tuition(year, program)
    return {"items": items}


@app.get("/hocbong")
async def get_scholarships(
    q: Optional[str] = Query(None, description="Tên học bổng để tìm kiếm")
):
    """
    Tra cứu học bổng.

    Tham số:
    - q: Từ khóa tìm kiếm (tên học bổng), optional

    Returns:
        {
            "items": [
                {
                    "ten_hoc_bong": str,
                    "doi_tuong": str,
                    "gia_tri": str,
                    "dieu_kien": str
                },
                ...
            ]
        }

    Example 1 - Tất cả học bổng:
        GET /hocbong

    Example 2 - Tìm học bổng khuyến khích:
        GET /hocbong?q=khuyến khích
    """
    try:
        logger.info(f"📚 /hocbong - Query: {q}")
        items = csvs.list_scholarships(q)
        logger.info(f"✅ /hocbong - Found {len(items)} scholarships")
        return {"items": items}
    except Exception as e:
        logger.error(f"❌ Error in /hocbong: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/chi-tieu")
async def get_quota(
    major: Optional[str] = Query(None, description="Tên hoặc mã ngành"),
    year: Optional[str] = Query(None, description="Năm học"),
):
    """
    Tra cứu chỉ tiêu tuyển sinh.

    Chỉ tiêu = số lượng sinh viên dự kiến tuyển cho mỗi ngành

    Tham số:
    - major: Tên hoặc mã ngành (optional)
    - year: Năm học (optional)

    Returns:
        {
            "items": [
                {
                    "ma_nganh": str,
                    "ten_nganh": str,
                    "nam": str,
                    "chi_tieu": int,        # Số lượng dự kiến tuyển
                    "phuong_thuc": str,     # Phương thức xét tuyển
                    "ghi_chu": str
                },
                ...
            ]
        }

    Example 1 - Chỉ tiêu tất cả ngành năm 2025:
        GET /chi-tieu?year=2025

    Example 2 - Chỉ tiêu ngành Kiến trúc:
        GET /chi-tieu?major=kiến trúc

    Example 3 - Chỉ tiêu ngành Kiến trúc năm 2025:
        GET /chi-tieu?major=kiến trúc&year=2025
    """
    try:
        logger.info(f"📊 /chi-tieu - Major: {major}, Year: {year}")

        # Đọc file CSV chỉ tiêu
        rows = csvs._read_csv(os.path.join(DATA_DIR, "admission_quota.csv"))

        # Nếu có filter, lọc dữ liệu
        if major or year:
            results = []
            for r in rows:
                ma = (r.get("ma_nganh") or "").lower()
                ten = (r.get("ten_nganh") or "").lower()
                nam = (r.get("nam") or "").lower()

                # Lọc theo ngành nếu có
                if major and major.lower() not in ma and major.lower() not in ten:
                    continue
                # Lọc theo năm nếu có
                if year and year not in nam:
                    continue

                results.append(r)

            logger.info(f"✅ /chi-tieu - Found {len(results)} records")
            return {"items": results}

        # Nếu không filter, trả tất cả
        logger.info(f"✅ /chi-tieu - Returning all {len(rows)} records")
        return {"items": rows}

    except Exception as e:
        logger.error(f"❌ Error in /chi-tieu: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/lich")
async def get_schedule(
    phuong_thuc: Optional[str] = Query(None, description="Phương thức xét tuyển")
):
    """
    Tra cứu lịch tuyển sinh (thời gian, các bước, deadline).

    Tham số:
    - phuong_thuc: Phương thức xét tuyển (optional)
        Ví dụ: "THPT", "Học bạ", "TSA", "ĐGNL", "Tuyển thẳng"

    Returns:
        {
            "items": [
                {
                    "phuong_thuc": str,     # Phương thức xét tuyển
                    "buoc": str,            # Bước trong quy trình
                    "bat_dau": str,         # Ngày bắt đầu
                    "ket_thuc": str,        # Ngày kết thúc/deadline
                    "mo_ta": str,           # Mô tả công việc cần làm
                    "url": str              # Link hướng dẫn chi tiết
                },
                ...
            ]
        }

    Example 1 - Lịch tất cả phương thức:
        GET /lich

    Example 2 - Lịch xét tuyển THPT:
        GET /lich?phuong_thuc=THPT

    Example 3 - Lịch xét học bạ:
        GET /lich?phuong_thuc=học bạ
    """
    try:
        logger.info(f"📅 /lich - Phuong thuc: {phuong_thuc}")

        # Đọc file CSV lịch tuyển sinh
        rows = csvs._read_csv(os.path.join(DATA_DIR, "admissions_schedule.csv"))

        # Lọc theo phương thức nếu có
        if phuong_thuc:
            rows = [
                r
                for r in rows
                if phuong_thuc.lower() in (r.get("phuong_thuc") or "").lower()
            ]

        logger.info(f"✅ /lich - Found {len(rows)} schedule entries")
        return {"items": rows}

    except Exception as e:
        logger.error(f"❌ Error in /lich: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/kenh-nop")
async def get_apply_channel(
    phuong_thuc: Optional[str] = Query(None, description="Phương thức xét tuyển")
):
    """
    Tra cứu kênh nộp hồ sơ (online, offline, qua bưu điện).

    Tham số:
    - phuong_thuc: Phương thức xét tuyển (optional)

    Returns:
        {
            "items": [
                {
                    "kenh": str,            # Tên kênh (Website, Bưu điện, Trực tiếp)
                    "phuong_thuc": str,     # Phương thức xét tuyển áp dụng
                    "url": str,             # Link website nộp hồ sơ
                    "dia_chi": str,         # Địa chỉ nộp trực tiếp
                    "huong_dan": str        # Hướng dẫn chi tiết
                },
                ...
            ]
        }

    Example 1 - Tất cả kênh nộp:
        GET /kenh-nop

    Example 2 - Kênh nộp cho THPT:
        GET /kenh-nop?phuong_thuc=THPT

    Ghi chú:
    - Mỗi phương thức có thể có nhiều kênh nộp
    - Website thường nhanh và tiện nhất
    - Nộp trực tiếp phù hợp nếu cần tư vấn trực tiếp
    """
    try:
        logger.info(f"📮 /kenh-nop - Phuong thuc: {phuong_thuc}")

        # Đọc file CSV kênh nộp hồ sơ
        rows = csvs._read_csv(os.path.join(DATA_DIR, "apply_channel.csv"))

        # Lọc theo phương thức nếu có
        if phuong_thuc:
            rows = [
                r
                for r in rows
                if phuong_thuc.lower() in (r.get("phuong_thuc") or "").lower()
            ]

        logger.info(f"✅ /kenh-nop - Found {len(rows)} channels")
        return {"items": rows}

    except Exception as e:
        logger.error(f"❌ Error in /kenh-nop: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/dieu-kien")
async def get_conditions(
    phuong_thuc: Optional[str] = Query(None, description="Phương thức xét tuyển"),
    year: Optional[str] = Query(None, description="Năm học"),
):
    """
    Tra cứu điều kiện xét tuyển cho từng phương thức.

    Tham số:
    - phuong_thuc: Phương thức xét tuyển (optional)
    - year: Năm học (optional)

    Returns:
        {
            "items": [
                {
                    "phuong_thuc": str,     # Phương thức xét tuyển
                    "nam": str,             # Năm áp dụng
                    "dieu_kien": str,       # Điều kiện cần đáp ứng
                    "loai_dieu_kien": str,  # Loại: bắt buộc/ưu tiên/bổ sung
                    "chi_tiet": str,        # Giải thích chi tiết
                    "vi_du": str            # Ví dụ minh họa
                },
                ...
            ]
        }

    Example 1 - Tất cả điều kiện năm 2025:
        GET /dieu-kien?year=2025

    Example 2 - Điều kiện xét tuyển thẳng:
        GET /dieu-kien?phuong_thuc=tuyển thẳng

    Example 3 - Điều kiện học bạ năm 2025:
        GET /dieu-kien?phuong_thuc=học bạ&year=2025

    Ghi chú:
    - Mỗi phương thức có điều kiện riêng
    - Điều kiện có thể thay đổi theo năm
    - Cần đọc kỹ để đảm bảo đủ điều kiện
    """
    try:
        logger.info(f"📋 /dieu-kien - Phuong thuc: {phuong_thuc}, Year: {year}")

        # Đọc file CSV điều kiện xét tuyển
        rows = csvs._read_csv(os.path.join(DATA_DIR, "admission_conditions.csv"))

        # Lọc theo phương thức và năm nếu có
        if phuong_thuc:
            rows = [
                r
                for r in rows
                if phuong_thuc.lower() in (r.get("phuong_thuc") or "").lower()
            ]
        if year:
            rows = [r for r in rows if year in (r.get("nam") or "")]

        logger.info(f"✅ /dieu-kien - Found {len(rows)} conditions")
        return {"items": rows}

    except Exception as e:
        logger.error(f"❌ Error in /dieu-kien: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ============================================================================
# PHẦN 6: ENDPOINTS - HELPER (Hỗ trợ)
# ============================================================================


@app.post("/goiy")
async def suggest_majors(req: Dict[str, Any]):
    """
    Gợi ý ngành học phù hợp dựa trên điểm số.

    Endpoint này giúp học sinh:
    - Tìm ngành có điểm chuẩn/sàn phù hợp với điểm của mình
    - Biết được các ngành có khả năng đỗ

    Args:
        req: Dict chứa:
            - score: Điểm số của học sinh (float)
            - score_type: "chuan" hoặc "san" (optional, mặc định "chuan")
            - year: Năm học (optional)

    Returns:
        {
            "items": [
                {
                    "ma_nganh": str,
                    "ten_nganh": str,
                    "diem_chuan" | "diem_san": float,
                    "khoi_thi": str
                },
                ...
            ],
            "message": str  # Thông báo cho user
        }

    Example Request:
        POST /goiy
        {
            "score": 25.5,
            "score_type": "chuan",
            "year": "2025"
        }

    Example Response:
        {
            "items": [
                {
                    "ma_nganh": "D510101",
                    "ten_nganh": "Kiến trúc",
                    "diem_chuan": 25.0,
                    "khoi_thi": "A00"
                },
                ...
            ],
            "message": "Tìm thấy 5 ngành có điểm chuẩn <= 25.5"
        }
    """
    try:
        # Log request
        logger.info(
            f"🎯 /goiy - Score: {req.get('score')}, Type: {req.get('score_type', 'chuan')}, Year: {req.get('year')}"
        )

        score = req.get("score")
        score_type = req.get("score_type", "chuan")
        year = req.get("year", "2025")

        # Validate score
        if not score:
            raise HTTPException(
                status_code=400, detail="Missing required parameter: score"
            )

        # Convert score to float
        try:
            score_float = float(score)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=400, detail="Invalid score value. Must be a number."
            )

        # Chuẩn bị request_data theo format mà csv_service expect
        # Function suggest_majors_by_score() expect Dict với keys:
        # - diem_thpt, diem_tsa, diem_dgnl (cho điểm các loại)
        # - chung_chi (cho chứng chỉ)
        # - nam (cho năm học)
        request_data = {"nam": year}

        # Tùy score_type, set vào key tương ứng
        if score_type == "san":
            # Điểm sàn không có trong suggest function hiện tại
            # Cần dùng logic riêng hoặc fallback sang điểm chuẩn
            request_data["diem_thpt"] = score_float
            logger.warning(
                f"⚠️ score_type='san' not fully supported yet, using 'chuan' logic"
            )
        else:
            # Mặc định dùng điểm THPT để so sánh điểm chuẩn
            request_data["diem_thpt"] = score_float

        # Gọi service để tìm ngành phù hợp
        items = csvs.suggest_majors_by_score(request_data)

        # Tạo message thông báo
        if items:
            message = f"Tìm thấy {len(items)} ngành có điểm {score_type} phù hợp với điểm {score}"
            logger.info(f"✅ /goiy - Found {len(items)} majors")
        else:
            message = (
                f"Không tìm thấy ngành có điểm {score_type} phù hợp với điểm {score}"
            )
            logger.info(f"⚠️ /goiy - No majors found")

        return {"items": items, "message": message}

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log và trả về lỗi 500
        logger.error(f"❌ Error in /goiy: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ============================================================================
# CHẠY ỨNG DỤNG
# ============================================================================
# Nếu chạy trực tiếp file này: python main.py
# (Thường không dùng, nên dùng uvicorn)
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
