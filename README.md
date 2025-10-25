# Chatbot Tư vấn Tuyển sinh HUCE

API Backend cho Chatbot tư vấn tuyển sinh Đại học Xây dựng Hà Nội.

## 📋 Tổng quan

Chatbot hỗ trợ học sinh và phụ huynh tra cứu thông tin tuyển sinh:
- Ngành học, khối thi, tổ hợp môn
- Điểm chuẩn, điểm sàn, chỉ tiêu
- Học phí, học bổng
- Phương thức xét tuyển
- Gợi ý ngành theo điểm số

## 🚀 Cài đặt & Chạy

### 1. Cài đặt uv

```bash
# Windows
pip install uv

# macOS/Linux  
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**🚀 Tại sao dùng uv?**
- ⚡ **Cực nhanh**: Nhanh hơn pip 10-100x (viết bằng Rust)
- 🤖 **Tự động**: Tự động cập nhật pyproject.toml, không cần chỉnh file thủ công
- 🔒 **Nhất quán**: Lock file đảm bảo team dùng cùng version dependencies
- 💾 **Tiết kiệm**: Cache toàn cục, không duplicate packages giữa các projects
- 🎯 **Thông minh**: Tự động resolve dependency conflicts


### 2. Cài đặt dependencies

```bash
cd backend
uv sync
```

### 3. Chạy server

```bash
# Từ thư mục backend
uv run uvicorn main:app --reload
```

Server chạy tại: http://localhost:8000

### 4. Xem API docs

Swagger UI: http://localhost:8000/docs

## 📁 Cấu trúc code

```
backend/
├── main.py                 # FastAPI app - TẤT CẢ endpoints
├── config.py              # Cấu hình (constants, thresholds)
├── services/
│   ├── nlp_service.py     # NLP + Context management
│   └── csv_service.py     # Xử lý dữ liệu CSV
├── nlu/                   # NLP core
│   ├── pipeline.py        # Điều phối NLP
│   ├── intent.py          # Intent detection (TF-IDF)
│   ├── entities.py        # Entity extraction
│   └── preprocess.py      # Text normalization
├── data/                  # Dữ liệu CSV
│   ├── major_intro.csv
│   ├── standard_score.csv
│   ├── floor_score.csv
│   ├── tuition.csv
│   ├── scholarships_huce.csv
│   ├── intent.csv
│   ├── entity.json
│   └── synonym.csv
└── test_backend.py        # Unit tests
```

## 📡 API Endpoints

### Health Check
```http
GET /
```

### Chat
```http
POST /chat
Body: {"message": "Điểm chuẩn ngành Kiến trúc"}
→ Phân tích NLP đơn giản

POST /chat/advanced
Body: {
  "message": "Còn điểm sàn?",
  "session_id": "user_123",
  "use_context": true
}
→ Chat đầy đủ với context

POST /chat/context
Body: {"action": "reset", "session_id": "user_123"}
→ Quản lý context (get/set/reset)
```

### Data
```http
GET /nganh?q=kiến trúc
→ Tra cứu ngành học

GET /diem?score_type=chuan&major=kiến trúc&year=2025
→ Điểm chuẩn/sàn

GET /hocphi?year=2025
→ Học phí

GET /hocbong?q=khuyến khích
→ Học bổng
```

### Helper
```http
POST /goiy
Body: {"score": 25.5, "score_type": "chuan", "year": "2025"}
→ Gợi ý ngành theo điểm
```

## 🧠 NLP Pipeline

### Intent Detection
- Phương pháp: TF-IDF + Cosine Similarity
- Dữ liệu: `data/intent.csv`
- Threshold: 0.35 (config.py)

### Entity Extraction
- Phương pháp: Pattern + Dictionary + Underthesea NER
- Dữ liệu: `data/entity.json`
- Entities: TEN_NGANH, MA_NGANH, KHOI_THI, DIEM_SO, NAM_HOC, ...

### Text Preprocessing
1. Normalize Unicode (VN diacritics)
2. Lowercase
3. Remove special chars
4. Tokenize (Underthesea)
5. Map synonyms (`data/synonym.csv`)

## 🔧 Cấu hình

File `config.py`:
```python
DATA_DIR = "data"                 # Thư mục chứa CSV
INTENT_THRESHOLD = 0.35           # Ngưỡng intent confidence
CONTEXT_HISTORY_LIMIT = 10        # Lưu 10 câu hội thoại
```

## 🧪 Testing

```bash
uv run pytest test_backend.py -v
```

## 📊 Dữ liệu CSV

| File | Mục đích |
|------|----------|
| `major_intro.csv` | Thông tin ngành học |
| `standard_score.csv` | Điểm chuẩn (2023-2025) |
| `floor_score.csv` | Điểm sàn theo phương thức |
| `tuition.csv` | Học phí |
| `scholarships_huce.csv` | Học bổng |
| `intent.csv` | Training data cho intent detection |
| `entity.json` | Dictionary cho entity extraction |
| `synonym.csv` | Từ đồng nghĩa, viết tắt |

## 💡 Luồng xử lý

```
User message → FastAPI endpoint
     ↓
NLPService.handle_message()
     ├── NLPPipeline.analyze()
     │   ├── Preprocess (normalize, tokenize)
     │   ├── Intent detection (TF-IDF)
     │   └── Entity extraction (pattern + NER)
     ├── Check confidence score
     │   ├── High → csv_service.handle_intent_query()
     │   └── Low  → csv_service.handle_fallback_query()
     └── Update context
         ├── Append to conversation history
         └── Save last_intent, last_entities
              ↓
         Response to user
```

## 🎯 Tính năng chính

### 1. Context Management
- Lưu 10 câu hội thoại gần nhất
- Hiểu câu hỏi tiếp theo dựa vào ngữ cảnh
- Reset context để bắt đầu hội thoại mới

### 2. Fallback thông minh
- Khi không nhận diện được intent rõ ràng
- Tìm kiếm theo từ khóa đơn giản
- Gợi ý cách hỏi rõ hơn

### 3. CSV Caching
- Cache dữ liệu CSV theo mtime
- Tự động reload khi file thay đổi
- Giảm 90% disk I/O

### 4. Multi-session support
- Mỗi user có session_id riêng
- Context tách biệt giữa các session
- Hỗ trợ nhiều user cùng lúc

## 🛠 Thêm tính năng mới

### 1. Thêm Intent mới

**Bước 1**: Thêm vào `data/intent.csv`
```csv
intent_name,sample_query
hoi_thoi_gian_xet_tuyen,khi nào xét tuyển
hoi_thoi_gian_xet_tuyen,thời gian nộp hồ sơ
```

**Bước 2**: Xử lý trong `csv_service.handle_intent_query()`
```python
if intent == "hoi_thoi_gian_xet_tuyen":
    data = _read_csv_cached(os.path.join(DATA_DIR, "admissions_schedule.csv"))
    return {"type": "schedule", "data": data}
```

### 2. Thêm Entity mới

Thêm vào `data/entity.json`:
```json
{
  "THOI_GIAN": {
    "patterns": ["\\d{1,2}/\\d{1,2}/\\d{4}"],
    "keywords": ["deadline", "hạn cuối", "thời hạn"]
  }
}
```

### 3. Thêm Endpoint mới

Thêm vào `main.py`:
```python
@app.get("/thoi-gian")
async def get_schedule():
    data = csvs.read_schedule()  # Thêm hàm này vào csv_service
    return {"items": data}
```

## 📈 Hiệu năng

- Response time: < 200ms (cached)
- Memory: ~100MB (với tất cả CSV loaded)
- Concurrent users: 50+ (FastAPI async)

## 🚧 TODO

- [ ] Thêm API điểm sàn theo chứng chỉ
- [ ] Thêm API cơ hội nghề nghiệp
- [ ] Tích hợp Redis cho context (production)
- [ ] Thêm logging
- [ ] Deployment Docker

## 📝 Lưu ý

1. **Context in-memory**: Hiện tại context lưu trong RAM, mất khi restart. Production nên dùng Redis.
2. **CSV caching**: Tự động reload khi file CSV thay đổi (check mtime).
3. **Underthesea**: Cần download model lần đầu: `uv run python -m underthesea download-fasttext-model`
4. **Encoding**: Tất cả CSV phải UTF-8 encoding.

## 👨‍💻 Development

### Chạy với hot reload
```bash
cd backend
uv run uvicorn main:app --reload --log-level debug
```

### Test một endpoint
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Điểm chuẩn ngành Kiến trúc"}'
```

### Debug NLP
```bash
uv run python
```
```python
>>> from services.nlp_service import get_nlp_service
>>> nlp = get_nlp_service()
>>> result = nlp.analyze_message("Điểm chuẩn ngành Kiến trúc")
>>> print(result)
```
