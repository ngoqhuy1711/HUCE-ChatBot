# API Backend - Chatbot Tư vấn Tuyển sinh HUCE

API Backend cho hệ thống Chatbot tư vấn tuyển sinh Đại học Xây dựng Hà Nội.

## 🎯 Tổng quan

Hệ thống cung cấp API NLP để tra cứu thông tin tuyển sinh:

- **Ngành học**: Danh sách ngành, mã ngành, khối thi, tổ hợp môn
- **Điểm số**: Điểm chuẩn, điểm sàn theo năm và ngành
- **Học phí & Học bổng**: Thông tin chi phí và các chương trình hỗ trợ (53 học bổng)
- **Phương thức xét tuyển**: Điều kiện, lịch trình, kênh nộp hồ sơ

### Công nghệ

- **Framework**: FastAPI (Python 3.13+)
- **NLP**: Underthesea (xử lý tiếng Việt)
- **Phương pháp**: TF-IDF + Cosine Similarity cho intent detection
- **Dữ liệu**: CSV files (13 files, dễ cập nhật)

---

## 🚀 Cài đặt

### 1. Cài đặt uv

```bash
# Windows
pip install uv

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Cài dependencies

```bash
cd backend
uv sync
```

### 3. (Tùy chọn) Cấu hình môi trường

```bash
cp env.example .env
# Chỉnh sửa .env nếu cần (CORS_ORIGINS, LOG_LEVEL, INTENT_THRESHOLD)
```

### 4. Chạy server

```bash
uv run uvicorn main:app --reload
```

- **Server**: <http://localhost:8000>
- **API Docs**: <http://localhost:8000/docs>

---

## 📡 API Endpoints

### 1. Health Check

```http
GET /
```

### 2. Chat (NLP)

**Chat với context:**

```http
POST /chat/advanced
Content-Type: application/json

{
  "message": "Điểm chuẩn ngành Kiến trúc năm 2025",
  "session_id": "user_123",
  "use_context": true
}
```

**Quản lý context:**

```http
POST /chat/context
Content-Type: application/json

{
  "action": "reset",      # get/set/reset
  "session_id": "user_123"
}
```

### Response Format

```json
{
  "type": "scholarships",
  "message": "🎁 Mình tìm thấy 53 suất học bổng...",
  "data": [...],
  "suggestions": [...]
}
```

---

## 🧠 Kiến trúc NLP

```text
Câu hỏi → Tiền xử lý → Intent Detection → Entity Extraction → Lấy dữ liệu CSV → Response
```

**Các bước:**

1. Tiền xử lý: Chuẩn hóa Unicode, tách từ, map từ đồng nghĩa
2. Intent Detection: TF-IDF + Cosine Similarity (ngưỡng: 0.35)
3. Entity Extraction: Pattern matching + Dictionary lookup + NER
4. Data Processing: Lấy dữ liệu từ CSV (có cache theo mtime)
5. Context Management: Lưu 10 câu gần nhất mỗi session

---

## 📂 Cấu trúc thư mục

```text
backend/
├── main.py                    # FastAPI app (3 endpoints)
├── config.py                  # Environment config
├── constants.py               # Intent/Entity constants
├── models.py                  # Pydantic models
│
├── nlu/                       # NLP core
│   ├── pipeline.py           # Điều phối NLP
│   ├── intent.py             # Intent detection
│   ├── entities.py           # Entity extraction
│   └── preprocess.py         # Tiền xử lý
│
├── services/
│   ├── nlp_service.py        # NLP service + Context
│   ├── csv_service.py        # Entry point cho CSV processing
│   ├── handlers/             # Intent handlers
│   │   ├── intent_handler.py
│   │   └── fallback.py
│   └── processors/           # Data processors
│       ├── admissions.py     # Phương thức, chỉ tiêu
│       ├── scores.py         # Điểm chuẩn/sàn
│       ├── academic.py       # Học phí, học bổng
│       ├── majors.py         # Ngành học
│       ├── contact.py        # Thông tin liên hệ
│       ├── cefr.py           # Chứng chỉ CEFR
│       ├── cache.py          # CSV caching
│       └── utils.py          # Utilities
│
├── data/                     # Dữ liệu CSV (13 files)
│   ├── intent.csv
│   ├── entity.json
│   ├── synonym.csv
│   ├── majors.csv
│   ├── admission_scores.csv
│   ├── admission_methods.csv
│   ├── admission_targets.csv
│   ├── admission_conditions.csv
│   ├── admissions_schedule.csv
│   ├── scholarships.csv      # 53 học bổng
│   ├── tuition.csv
│   ├── subject_combinations.csv
│   └── contact_info.csv
│
└── tools/
    └── generate_intents.py   # Tool tạo intent.csv
```

---

## 🔧 Cấu hình

### Environment Variables (`.env`)

```env
# NLP
INTENT_THRESHOLD=0.35
CONTEXT_HISTORY_LIMIT=10

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080
```

---

## 🎓 Tính năng

### 1. Context Management

- Lưu 10 câu hội thoại gần nhất mỗi session
- Hiểu câu hỏi tiếp theo dựa vào ngữ cảnh

**Ví dụ:**

```text
User: "Điểm chuẩn ngành Kiến trúc?"
Bot: "25.5 điểm"
User: "Còn điểm sàn?"  ← Bot hiểu "Kiến trúc" từ context
Bot: "22.0 điểm"
```

### 2. Fallback thông minh

- Tự động tìm kiếm theo từ khóa khi không nhận diện được intent
- Gợi ý cách hỏi rõ hơn

### 3. CSV Caching

- Cache dữ liệu CSV theo modification time
- Tự động reload khi file thay đổi
- Giảm 90% I/O operations

---

## 🧪 Testing

```bash
# Test health check
curl http://localhost:8000/

# Test chat
curl -X POST http://localhost:8000/chat/advanced \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Điểm chuẩn ngành Kiến trúc",
    "session_id": "test_123",
    "use_context": true
  }'
```

---

## 📝 Lưu ý

### Developer

- **Python**: 3.13+
- **Encoding**: Tất cả CSV phải UTF-8
- **Context**: Lưu trong RAM (mất khi restart)
- **Production**: Nên dùng Redis cho context store

### Frontend

- **CORS**: Đã config sẵn cho React (3000), Vite (5173), Reflex (8080)
- **Session ID**: Generate unique ID cho mỗi user
- **Response**: Luôn check `response.type` và `response.message`

### Performance

- **Response time**: < 200ms (với cache)
- **Memory**: ~100MB
- **Concurrent users**: 50+ (FastAPI async)

---

## 🐛 Troubleshooting

### Server không start

```bash
uv run python -c "import main; print('OK')"
cat logs/chatbot.log
```

### CORS errors

```bash
# Thêm origin vào .env
echo "CORS_ORIGINS=http://localhost:8080" >> .env
```

### NLP không chính xác

- Kiểm tra `data/intent.csv` có đủ mẫu câu
- Điều chỉnh `INTENT_THRESHOLD` trong .env
- Thêm từ đồng nghĩa vào `data/synonym.csv`

---

## 📞 Hỗ trợ

- **API Docs**: <http://localhost:8000/docs>
- **Logs**: `backend/logs/chatbot.log`

---

**Phiên bản**: 1.0.0  
**Ngày cập nhật**: 2025-11-12  
**Trạng thái**: Production Ready ✅
