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
   GET  /nganh   → Danh sách ngành học
   GET  /diem    → Điểm chuẩn/điểm sàn
   GET  /hocphi  → Học phí
   GET  /hocbong → Học bổng

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
- Dự án nhỏ (9 endpoints) → 1 file dễ quản lý hơn
- Debug nhanh hơn (không nhảy qua nhiều file)
- Đơn giản hơn cho 1 người maintain
- Vẫn rõ ràng với comment đầy đủ
"""

from typing import Optional, Dict, Any
from fastapi import FastAPI, Query
from pydantic import BaseModel

# Import services
from services.nlp_service import get_nlp_service
from services import csv_service as csvs


# ============================================================================
# PHẦN 1: KHỞI TẠO ỨNG DỤNG FASTAPI
# ============================================================================

app = FastAPI(
    title="HUCE Admissions Chatbot API",
    description="API cho Chatbot tư vấn tuyển sinh Đại học Xây dựng Hà Nội",
    version="1.0.0"
)

# Lấy NLP service singleton
# Service này chứa: pipeline (NLP), context_store (lưu context)
# Được khởi tạo MỘT LẦN khi app start, dùng chung cho mọi request
nlp = get_nlp_service()


# ============================================================================
# PHẦN 2: PYDANTIC MODELS - Định nghĩa cấu trúc dữ liệu
# ============================================================================

class ChatRequest(BaseModel):
    """
    Request cho endpoint /chat (phân tích NLP đơn giản).
    
    Attributes:
        message: Câu hỏi từ người dùng
        
    Example:
        {"message": "Điểm chuẩn ngành Kiến trúc"}
    """
    message: str


class AdvancedChatRequest(BaseModel):
    """
    Request cho endpoint /chat/advanced (chat đầy đủ).
    
    Attributes:
        message: Câu hỏi từ người dùng
        session_id: ID phiên hội thoại (để lưu context riêng từng user)
        use_context: Có sử dụng context hay không
        
    Example:
        {
            "message": "Còn điểm sàn?",
            "session_id": "user_abc_123",
            "use_context": true
        }
    """
    message: str
    session_id: Optional[str] = "default"
    use_context: Optional[bool] = True


# ============================================================================
# PHẦN 3: ENDPOINTS - HEALTH CHECK
# ============================================================================

@app.get("/")
async def root():
    """
    Health check endpoint - Kiểm tra server hoạt động.
    
    Returns:
        {"message": "HUCE Chatbot API is running"}
        
    Usage:
        curl http://localhost:8000/
    """
    return {"message": "HUCE Chatbot API is running"}


# ============================================================================
# PHẦN 4: ENDPOINTS - CHAT (Hội thoại)
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
            "intent": str,      # Ý định nhận diện
            "score": float,     # Độ tin cậy 0-1
            "entities": list    # Entities trích xuất
        }
        
    Example Request:
        POST /chat
        {"message": "Điểm chuẩn ngành Kiến trúc 2025"}
        
    Example Response:
        {
            "intent": "hoi_diem_chuan",
            "score": 0.85,
            "entities": [
                {"label": "TEN_NGANH", "text": "kiến trúc"},
                {"label": "NAM_HOC", "text": "2025"}
            ]
        }
    """
    analysis = nlp.analyze_message(req.message)
    return analysis


@app.post("/chat/context")
async def manage_chat_context(req: Dict[str, Any]):
    """
    Quản lý context hội thoại - get/set/reset.
    
    Context giúp bot "nhớ" cuộc trò chuyện để xử lý câu hỏi tiếp theo.
    
    Các action:
    - "get": Lấy context hiện tại
    - "set": Đặt context mới
    - "reset": Xóa context (bắt đầu hội thoại mới)
    
    Args:
        req: Dict chứa:
            - action: "get" | "set" | "reset"
            - session_id: ID phiên (mặc định "default")
            - context: Context mới (chỉ khi action="set")
            
    Returns:
        - GET: {"context": {...}}
        - SET: {"message": "Context updated", "context": {...}}
        - RESET: {"message": "Context reset"}
        
    Example 1 - Get context:
        POST /chat/context
        {"action": "get", "session_id": "user_123"}
        
    Example 2 - Reset context:
        POST /chat/context
        {"action": "reset", "session_id": "user_123"}
    """
    action = req.get("action", "get")
    session_id = req.get("session_id", "default")
    
    if action == "get":
        # Lấy context của session
        context = nlp.get_context(session_id)
        return {"context": context}
    
    elif action == "set":
        # Đặt context mới
        context = req.get("context", {})
        nlp.set_context(session_id, context)
        return {"message": "Context updated", "context": context}
    
    elif action == "reset":
        # Xóa context (bắt đầu hội thoại mới)
        nlp.reset_context(session_id)
        return {"message": "Context reset"}
    
    else:
        # Action không hợp lệ
        return {"error": "Invalid action. Use: get, set, or reset"}


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
    │ 3. Cập nhật context với câu hỏi mới     │
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
    message = req.message
    session_id = req.session_id or "default"
    use_context = req.use_context if req.use_context is not None else True
    
    # Bước 1: Lấy context hiện tại (nếu dùng context)
    current_context = nlp.get_context(session_id) if use_context else {}
    
    # Bước 2: Xử lý message (NLP + dữ liệu + fallback)
    result = nlp.handle_message(message, current_context)
    analysis = result["analysis"]
    response = result["response"]
    
    # Bước 3: Cập nhật context
    # Thêm câu hỏi-trả lời vào lịch sử
    new_context = nlp.append_history(session_id, {
        "message": message,
        "intent": analysis["intent"],
        "response": response
    })
    # Lưu intent và entities của câu hiện tại
    new_context["last_intent"] = analysis["intent"]
    new_context["last_entities"] = analysis["entities"]
    
    # Bước 4: Trả về kết quả đầy đủ
    return {
        "analysis": analysis,
        "response": response,
        "context": new_context
    }


# ============================================================================
# PHẦN 5: ENDPOINTS - DATA (Tra cứu dữ liệu)
# ============================================================================

@app.get("/nganh")
async def get_majors(q: Optional[str] = Query(None, description="Tên hoặc mã ngành để tìm kiếm")):
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
    score_type: str = Query("chuan", description="Loại điểm: 'chuan' (điểm chuẩn) hoặc 'san' (điểm sàn)"),
    major: Optional[str] = Query(None, description="Tên hoặc mã ngành"),
    year: Optional[str] = Query(None, description="Năm học, ví dụ: 2025")
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
    program: Optional[str] = Query(None, description="Chương trình đào tạo")
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
async def get_scholarships(q: Optional[str] = Query(None, description="Tên học bổng để tìm kiếm")):
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
    items = csvs.list_scholarships(q)
    return {"items": items}


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
    score = req.get("score")
    score_type = req.get("score_type", "chuan")
    year = req.get("year")
    
    # Gọi service để tìm ngành phù hợp
    items = csvs.suggest_majors_by_score(score, score_type, year)
    
    # Tạo message thông báo
    if items:
        message = f"Tìm thấy {len(items)} ngành có điểm {score_type} phù hợp với điểm {score}"
    else:
        message = f"Không tìm thấy ngành có điểm {score_type} phù hợp với điểm {score}"
    
    return {
        "items": items,
        "message": message
    }


# ============================================================================
# CHẠY ỨNG DỤNG
# ============================================================================
# Nếu chạy trực tiếp file này: python main.py
# (Thường không dùng, nên dùng uvicorn)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
