# Chatbot Tư vấn Tuyển sinh HUCE

Giải pháp full-stack cung cấp trợ lý ảo hỗ trợ thí sinh tra cứu thông tin tuyển sinh Đại học Xây dựng Hà Nội (HUCE). Dự án gồm:

- **Backend API (FastAPI)**: Xử lý NLP tiếng Việt, truy vấn dữ liệu tuyển sinh từ CSV, quản lý ngữ cảnh hội thoại.
- **Frontend (Reflex)**: Giao diện web realtime, tích hợp WebSocket để hiển thị hội thoại với chatbot.

---

## Tính năng chính

- **Tra cứu tuyển sinh**: Ngành học, mã ngành, tổ hợp môn, chỉ tiêu, lịch xét tuyển.
- **Điểm chuẩn & điểm sàn**: Phân theo ngành, năm tuyển sinh; hỗ trợ so sánh nhanh.
- **Học phí & học bổng**: 53 chương trình hỗ trợ, cập nhật theo năm học.
- **Quản lý ngữ cảnh**: Lưu 10 lượt hội thoại gần nhất, hiểu câu hỏi tiếp nối.
- **Fallback thông minh**: Gợi ý cách đặt câu hỏi khi không phân loại được intent.
- **Giao diện realtime**: Frontend Reflex đồng bộ với backend qua API/WebSocket.

---

## Công nghệ

- **Backend**
  - FastAPI (Python 3.13+)
  - Underthesea cho xử lý tiếng Việt (tokenizer, POS)
  - TF-IDF + Cosine Similarity cho intent detection
  - Bộ dữ liệu CSV (13 file) với caching theo `mtime`

- **Frontend**
  - [Reflex](https://reflex.dev/) (Python 3.10+)
  - State management realtime qua WebSocket
  - Component tùy chỉnh (chat bubble, suggested questions)

---

## Cấu trúc thư mục

```text
├── config.py                 # Cấu hình backend (FastAPI)
├── constants.py              # Hằng số cho intents/entities
├── data/                     # Dữ liệu CSV tuyển sinh
├── main.py                   # Entry point FastAPI
├── models.py                 # Pydantic models cho API
├── nlu/                      # Pipeline NLP (tiền xử lý, intent, entity)
├── services/                 # Business logic & intent handlers
├── frontend/                 # Mã nguồn Reflex frontend
│   ├── chatbot/              # Ứng dụng Reflex (components, state, API client)
│   └── rxconfig.py           # Cấu hình Reflex (port, backend URL)
├── tools/                    # Tiện ích (generate intents, test queries)
├── README.md
└── uv.lock
```

---

## Bắt đầu

### 1. Chuẩn bị

- Python 3.13+ (cho cả backend và frontend)
- [uv](https://github.com/astral-sh/uv) để quản lý môi trường (khuyến nghị)

```bash
pip install uv
```

### 2. Cài đặt dependencies

```bash
cd C:\Users\ngoqh\DATN
uv sync

# (Tùy chọn) Tạo file môi trường
cp env.example .env
# Cập nhật các biến nếu cần (CORS_ORIGINS, LOG_LEVEL, INTENT_THRESHOLD)
```

> Lưu ý: Tất cả dependencies (backend + frontend) được cài đặt trong một môi trường duy nhất.

---

## Chạy ứng dụng

### Backend (FastAPI)

```bash
cd C:\Users\ngoqh\DATN
uv run uvicorn main:app --reload
```

- REST API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- Log: `logs/chatbot.log`

### Frontend (Reflex)

```bash
cd C:\Users\ngoqh\DATN\frontend
uv run reflex run
```

- Frontend dev server: `http://localhost:3000`
- WebSocket backend (Reflex): `ws://localhost:8001`
- Cấu hình kết nối backend nằm trong `frontend/rxconfig.py`

> Lưu ý: Cả backend và frontend đều chạy từ cùng một môi trường Python (root `.venv`).

---

## Cấu hình & biến môi trường

### Backend `.env`

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

### Frontend

- Sử dụng `frontend/rxconfig.py` để chỉnh `backend_url`, `port`, `backend_port`.
- Hỗ trợ `.env` (thông qua `python-dotenv`) nếu cần override cấu hình runtime.

---

## Kiến trúc NLP (Backend)

```text
Câu hỏi -> Tiền xử lý -> Intent Detection -> Entity Extraction -> Lấy dữ liệu CSV -> Response
```

1. **Tiền xử lý**: Chuẩn hóa Unicode, tách từ, ánh xạ từ đồng nghĩa (`data/synonym.csv`).
2. **Intent Detection**: TF-IDF vectorization + Cosine Similarity (ngưỡng 0.35).
3. **Entity Extraction**: Pattern matching + dictionary lookup + NER.
4. **Data Processing**: Đọc CSV với caching theo `mtime`.
5. **Context Management**: Lưu tối đa 10 câu gần nhất cho mỗi `session_id`.

---

## Kiểm thử nhanh

```bash
# 1. Health check
curl http://localhost:8000/

# 2. Chat API
curl -X POST http://localhost:8000/chat/advanced ^
  -H "Content-Type: application/json" ^
  -d "{
        \"message\": \"Điểm chuẩn ngành Kiến trúc\",
        \"session_id\": \"test_123\",
        \"use_context\": true
      }"
```

Trong giao diện Reflex, nhập câu hỏi trực tiếp tại `http://localhost:3000`.

---

## Vận hành & tối ưu

- **Context store**: Lưu trong RAM; khi triển khai production nên chuyển sang Redis.
- **Hiệu năng**: Thời gian phản hồi < 200ms (với cache), ~100MB RAM, hỗ trợ 50+ người dùng đồng thời.
- **Mở rộng dữ liệu**: Cập nhật các file CSV trong thư mục `data/`, hệ thống tự reload khi `mtime` thay đổi.

---

## Troubleshooting

- **Backend không khởi động**:
  ```bash
  uv run python -c "import main; print('OK')"
  type logs\chatbot.log
  ```
- **Frontend không kết nối được backend**:
  - Kiểm tra `backend_url` trong `frontend/rxconfig.py`.
  - Đảm bảo backend chạy tại `http://localhost:8000`.
- **Lỗi CORS**: Bổ sung origin mới vào `.env` rồi restart backend.
- **NLP trả về sai ý định**:
  - Tăng/giảm `INTENT_THRESHOLD`.
  - Bổ sung câu mẫu trong `data/intent.csv` và từ đồng nghĩa trong `data/synonym.csv`.

---

## Đóng góp

- Tạo branch mới cho mỗi tính năng/bugfix.
- Viết mô tả ngắn gọn, đính kèm lệnh kiểm thử đã chạy.
- Với thay đổi dữ liệu CSV, nhớ mô tả nguồn dữ liệu và ngày cập nhật.

---

## Hỗ trợ

- API Docs: `http://localhost:8000/docs`
- Issues/bugs: mở ticket hoặc liên hệ team NLP
- Log vận hành: `logs/chatbot.log`

---

**Phiên bản**: 1.0.0  
**Ngày cập nhật**: 2025-11-12  
**Trạng thái**: Production Ready
