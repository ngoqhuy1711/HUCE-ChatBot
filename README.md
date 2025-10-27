# API Backend - Chatbot Tư vấn Tuyển sinh HUCE

API Backend cho hệ thống Chatbot tư vấn tuyển sinh Đại học Xây dựng Hà Nội.

## 🎯 Tổng quan

Hệ thống cung cấp API để tra cứu thông tin tuyển sinh:
- **Ngành học**: Danh sách ngành, mã ngành, khối thi, tổ hợp môn
- **Điểm số**: Điểm chuẩn, điểm sàn theo năm và ngành
- **Học phí & Học bổng**: Thông tin chi phí và các chương trình hỗ trợ
- **Phương thức xét tuyển**: Điều kiện, lịch trình, kênh nộp hồ sơ
- **Gợi ý thông minh**: Đề xuất ngành phù hợp theo điểm số

### Công nghệ sử dụng
- **Framework**: FastAPI (Python 3.13+)
- **NLP**: Underthesea (xử lý tiếng Việt)
- **Phương pháp**: TF-IDF + Cosine Similarity cho intent detection
- **Dữ liệu**: CSV files (dễ cập nhật, không cần database)

---

## 🚀 Hướng dẫn cài đặt

### Bước 1: Cài đặt uv (package manager)

**Windows:**
```bash
pip install uv
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Bước 2: Cài dependencies

```bash
cd backend
uv sync
```

### Bước 3: (Tùy chọn) Cấu hình môi trường

```bash
# Copy file mẫu
cp env.example .env

# Chỉnh sửa .env nếu cần thay đổi:
# - CORS_ORIGINS: Địa chỉ frontend
# - LOG_LEVEL: Mức độ log (DEBUG/INFO/WARNING)
# - INTENT_THRESHOLD: Ngưỡng nhận diện intent (0-1)
```

### Bước 4: Chạy server

```bash
uv run uvicorn main:app --reload
```

Server chạy tại: **http://localhost:8000**

API Documentation: **http://localhost:8000/docs**

---

## 📡 API Endpoints

### 1. Kiểm tra hệ thống
```http
GET /
```
Kiểm tra server hoạt động

### 2. Chat & NLP

**Phân tích NLP đơn giản:**
```http
POST /chat
Content-Type: application/json

{
  "message": "Điểm chuẩn ngành Kiến trúc"
}
```

**Chat đầy đủ (có context):**
```http
POST /chat/advanced
Content-Type: application/json

{
  "message": "Còn điểm sàn thì sao?",
  "session_id": "user_123",
  "use_context": true
}
```

**Quản lý context:**
```http
POST /chat/context
Content-Type: application/json

{
  "action": "reset",           # get/set/reset
  "session_id": "user_123"
}
```

### 3. Tra cứu dữ liệu

| Endpoint | Mô tả | Query params |
|----------|-------|--------------|
| `GET /nganh` | Danh sách ngành | `?q=kiến trúc` |
| `GET /diem` | Điểm chuẩn/sàn | `?score_type=chuan&major=kiến trúc&year=2025` |
| `GET /hocphi` | Học phí | `?year=2025` |
| `GET /hocbong` | Học bổng | `?q=khuyến khích` |
| `GET /chi-tieu` | Chỉ tiêu tuyển sinh | `?major=kiến trúc&year=2025` |
| `GET /lich` | Lịch tuyển sinh | `?phuong_thuc=THPT` |
| `GET /kenh-nop` | Kênh nộp hồ sơ | `?phuong_thuc=THPT` |
| `GET /dieu-kien` | Điều kiện xét tuyển | `?phuong_thuc=THPT&year=2025` |

### 4. Gợi ý ngành

```http
POST /goiy
Content-Type: application/json

{
  "score": 25.5,
  "score_type": "chuan",       # chuan hoặc san
  "year": "2025"
}
```

---

## 🧠 Kiến trúc NLP

### Luồng xử lý
```
Câu hỏi người dùng
    ↓
[1] Tiền xử lý văn bản
    - Chuẩn hóa Unicode (tiếng Việt)
    - Lowercase, loại ký tự đặc biệt
    - Tách từ (Underthesea)
    - Map từ đồng nghĩa
    ↓
[2] Nhận diện Intent
    - TF-IDF + Cosine Similarity
    - Ngưỡng: 0.35 (config)
    - Fallback nếu không đạt ngưỡng
    ↓
[3] Trích xuất Entity
    - Pattern matching
    - Dictionary lookup (CSV)
    - NER (Underthesea)
    ↓
[4] Lấy dữ liệu từ CSV
    - Dựa vào intent + entities
    - Cache thông minh (mtime)
    ↓
[5] Cập nhật Context
    - Lưu lịch sử 10 câu gần nhất
    - Lưu intent + entities
    ↓
Trả về kết quả
```

### Dữ liệu huấn luyện

| File | Mục đích |
|------|----------|
| `intent.csv` | Mẫu câu cho intent detection |
| `entity.json` | Pattern cho entity extraction |
| `synonym.csv` | Từ đồng nghĩa, viết tắt |
| `major_intro.csv` | Thông tin ngành học |
| `standard_score.csv` | Điểm chuẩn 2023-2025 |
| `floor_score.csv` | Điểm sàn theo phương thức |
| `tuition.csv` | Học phí |
| `scholarships_huce.csv` | Học bổng |

---

## 🔧 Cấu hình

### Config từ Environment Variables

Tạo file `.env` từ `env.example`:

```bash
# NLP
INTENT_THRESHOLD=0.35              # Ngưỡng nhận diện intent (0-1)
CONTEXT_HISTORY_LIMIT=10           # Số câu lưu trong context

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=false
LOG_LEVEL=INFO                     # DEBUG/INFO/WARNING/ERROR

# CORS (Frontend origins)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# API
MAX_RESULTS=100                    # Giới hạn kết quả trả về
MAX_SUGGESTIONS=20                 # Giới hạn gợi ý ngành
```

### Config trong Code

File `constants.py` chứa tất cả hằng số:
- Intent names
- Entity labels
- Response types
- Error messages
- Validation rules

---

## 🧪 Testing

### Chạy test suite

```bash
# Start server trước
uv run uvicorn main:app --reload

# Terminal khác: chạy tests
uv run python test_api_comprehensive.py
```

### Test thủ công

```bash
# Test health check
curl http://localhost:8000/

# Test chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Điểm chuẩn ngành Kiến trúc"}'

# Test với session
curl -X POST http://localhost:8000/chat/advanced \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Còn điểm sàn?",
    "session_id": "test_123",
    "use_context": true
  }'
```

---

## 📂 Cấu trúc thư mục

```
backend/
│
├── 📄 Core
│   ├── main.py              # FastAPI application, tất cả endpoints
│   ├── config.py            # Cấu hình environment variables
│   ├── constants.py         # Intent/Entity/Error constants
│   └── models.py            # Pydantic request/response models
│
├── 📦 Services
│   ├── services/
│   │   ├── nlp_service.py   # NLP pipeline + Context management
│   │   └── csv_service.py   # Xử lý dữ liệu CSV
│   │
│   └── nlu/                 # NLP core modules
│       ├── pipeline.py      # Điều phối NLP
│       ├── intent.py        # Intent detection (TF-IDF)
│       ├── entities.py      # Entity extraction
│       └── preprocess.py    # Tiền xử lý văn bản
│
├── 📊 Data
│   └── data/                # Dữ liệu CSV (19 files)
│       ├── intent.csv
│       ├── entity.json
│       ├── synonym.csv
│       ├── major_intro.csv
│       ├── standard_score.csv
│       └── ...
│
└── 🛠 Support
    ├── env.example          # Template environment variables
    ├── test_api_comprehensive.py  # Test suite
    ├── pyproject.toml       # Dependencies
    └── README.md            # File này
```

---

## 🎓 Tính năng nâng cao

### 1. Context Management
- Lưu 10 câu hội thoại gần nhất mỗi session
- Hiểu câu hỏi tiếp theo dựa vào ngữ cảnh
- Mỗi user có `session_id` riêng

**Ví dụ:**
```
User: "Điểm chuẩn ngành Kiến trúc?"
Bot: "25.5 điểm"
User: "Còn điểm sàn?"         ← Bot hiểu "Kiến trúc" từ context
Bot: "22.0 điểm"
```

### 2. Fallback thông minh
- Khi không nhận diện được intent rõ ràng (score < 0.35)
- Tự động tìm kiếm theo từ khóa
- Gợi ý cách hỏi rõ hơn

### 3. CSV Caching
- Cache dữ liệu CSV theo modification time
- Tự động reload khi file thay đổi
- Giảm 90% I/O operations

### 4. Response chuẩn hóa
Tất cả endpoints trả về format nhất quán:
```json
{
  "success": true,
  "data": [...],
  "count": 10,
  "message": "Tìm thấy 10 kết quả"
}
```

---

## 📝 Lưu ý quan trọng

### Cho Developer
- **Python version**: Yêu cầu 3.13+
- **Encoding**: Tất cả CSV phải UTF-8
- **Context**: Lưu trong RAM, mất khi restart server
- **Production**: Nên dùng Redis cho context store

### Cho Frontend Developer
- **CORS**: Đã config sẵn cho React (3000), Vite (5173), Reflex (8080)
- **Response format**: Luôn check `response.success` trước khi xử lý data
- **Session ID**: Generate unique ID cho mỗi user để lưu context
- **Error handling**: 
  - 400: Bad request
  - 422: Validation error
  - 500: Server error

### Performance
- **Response time**: < 200ms (với cache)
- **Memory**: ~100MB (tất cả CSV loaded)
- **Concurrent users**: 50+ (FastAPI async)

---

## 🐛 Troubleshooting

### Server không start
```bash
# Kiểm tra import
uv run python -c "import main; print('OK')"

# Xem logs
cat logs/chatbot.log
```

### CORS errors
```bash
# Thêm origin vào .env
echo "CORS_ORIGINS=http://localhost:8080" >> .env
```

### NLP không chính xác
- Kiểm tra file `data/intent.csv` có đủ mẫu câu
- Điều chỉnh `INTENT_THRESHOLD` trong .env
- Thêm từ đồng nghĩa vào `data/synonym.csv`

### Tests fail
```bash
# Đảm bảo server đang chạy
curl http://localhost:8000/

# Kiểm tra logs
tail -f logs/chatbot.log
```

---

## 📞 Hỗ trợ

- **API Docs**: http://localhost:8000/docs
- **Logs**: `backend/logs/chatbot.log`
- **Test Suite**: `uv run python test_api_comprehensive.py`

---

**Phiên bản**: 1.0.0  
**Ngày cập nhật**: 2025-10-27  
**Trạng thái**: Production Ready ✅
