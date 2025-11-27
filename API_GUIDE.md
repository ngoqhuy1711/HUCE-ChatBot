# Tài Liệu API - HUCE Chatbot

**Phiên bản:** 1.0.0  
**Cập nhật:** 2025-11-25

---

## 📚 Mục Lục

1. [Tổng Quan](#tổng-quan)
2. [URL Cơ Bản](#url-cơ-bản)
3. [Định Dạng Response](#định-dạng-response)
4. [Endpoints](#endpoints)
5. [Xử Lý Lỗi](#xử-lý-lỗi)
6. [Ví Dụ](#ví-dụ)

---

## 📖 Tổng Quan

HUCE Chatbot API cung cấp các endpoint cho:

- **Tương tác chat** với phân tích NLP và quản lý context
- **Quản lý context** cho lịch sử hội thoại
- **Truy vấn dữ liệu** tuyển sinh

### Tính Năng Chính

- ✅ Xử lý Ngôn ngữ Tự nhiên tiếng Việt
- ✅ Hội thoại có nhận thức context
- ✅ Xử lý lỗi toàn diện
- ✅ Tracking request với ID duy nhất
- ✅ Làm sạch và validate input

---

## 🌐 URL Cơ Bản

```
Development: http://localhost:8000
Production:  https://api.huce-chatbot.com
```

---

## 🔄 Định Dạng Response

### Response Thành Công

```json
{
  "success": true,
  "message": "Thao tác hoàn thành thành công",
  "data": [...],
  "context": {...}
}
```

### Response Lỗi

```json
{
  "success": false,
  "error_code": "MÃ_LỖI",
  "error_message": "Thông báo lỗi dễ hiểu",
  "details": {...},
  "request_id": "uuid-string",
  "timestamp": "2025-11-25T10:00:00Z"
}
```

---

## 📡 Endpoints

### 1. Kiểm Tra Sức Khỏe

**GET** `/`

Kiểm tra xem API có đang hoạt động không.

**Response:**

```json
{
  "success": true,
  "message": "HUCE Chatbot API đang hoạt động"
}
```

**Ví dụ:**

```bash
curl http://localhost:8000/
```

---

### 2. Chat Nâng Cao

**POST** `/chat/advanced`

Endpoint chatbot chính với đầy đủ NLP, lấy dữ liệu và quản lý context.

**Request Body:**

```json
{
  "message": "Điểm chuẩn ngành Kiến trúc?",
  "session_id": "user_123",
  "use_context": true
}
```

**Tham Số:**

- `message` (string, bắt buộc): Câu hỏi (1-1000 ký tự)
- `session_id` (string, tùy chọn): ID phiên (default: "default")
- `use_context` (boolean, tùy chọn): Bật context (default: true)

**Response:**

```json
{
  "analysis": {
    "intent": "hoi_diem_chuan",
    "score": 0.95,
    "entities": [
      {
        "label": "TEN_NGANH",
        "text": "kiến trúc",
        "source": "pattern"
      }
    ]
  },
  "response": {
    "type": "standard_score",
    "data": [
      {
        "program_name": "Kiến trúc",
        "2024": "25.5",
        "subject_combination": "A00"
      }
    ],
    "message": "Điểm chuẩn ngành Kiến trúc năm 2024"
  },
  "context": {
    "last_intent": "hoi_diem_chuan",
    "last_entities": [...],
    "conversation_history": [...]
  }
}
```

**Các Loại Intent:**

- `hoi_diem_chuan`: Hỏi điểm chuẩn
- `hoi_hoc_phi`: Hỏi học phí
- `hoi_hoc_bong`: Hỏi học bổng
- `hoi_nganh`: Hỏi thông tin ngành
- `hoi_chi_tieu`: Hỏi chỉ tiêu tuyển sinh
- `hoi_phuong_thuc`: Hỏi phương thức tuyển sinh
- `hoi_dieu_kien`: Hỏi điều kiện tuyển sinh
- `fallback`: Không xác định được intent

**Ví Dụ:**

```bash
# Truy vấn cơ bản
curl -X POST http://localhost:8000/chat/advanced \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Điểm chuẩn ngành CNTT?",
    "session_id": "user_123"
  }'

# Câu hỏi tiếp theo với context
curl -X POST http://localhost:8000/chat/advanced \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Còn học phí thế nào?",
    "session_id": "user_123",
    "use_context": true
  }'
```

---

### 3. Quản Lý Context

**POST** `/chat/context`

Quản lý context hội thoại cho một phiên.

**Request Body:**

```json
{
  "action": "get|set|reset",
  "session_id": "user_123",
  "context": {...}
}
```

**Tham Số:**

- `action` (string, bắt buộc): `get`, `set`, hoặc `reset`
- `session_id` (string, tùy chọn): ID phiên (default: "default")
- `context` (object, tùy chọn): Data context (cần cho `set`)

**Response (GET):**

```json
{
  "success": true,
  "context": {
    "last_intent": "hoi_diem_chuan",
    "last_entities": [...],
    "conversation_history": [...]
  }
}
```

**Response (RESET):**

```json
{
  "success": true,
  "message": "Context đã được reset"
}
```

**Ví Dụ:**

```bash
# Lấy context
curl -X POST http://localhost:8000/chat/context \
  -H "Content-Type: application/json" \
  -d '{
    "action": "get",
    "session_id": "user_123"
  }'

# Reset context
curl -X POST http://localhost:8000/chat/context \
  -H "Content-Type: application/json" \
  -d '{
    "action": "reset",
    "session_id": "user_123"
  }'
```

---

## ⚠️ Xử Lý Lỗi

### Mã Lỗi

| Mã                        | Mô Tả                        | HTTP Status |
|---------------------------|------------------------------|-------------|
| `VALIDATION_ERROR`        | Dữ liệu request không hợp lệ | 422         |
| `DATA_NOT_FOUND`          | Không tìm thấy dữ liệu       | 422         |
| `INTENT_NOT_FOUND`        | Không xác định được intent   | 422         |
| `ENTITY_EXTRACTION_ERROR` | Lỗi trích xuất entity        | 422         |
| `CONTEXT_ERROR`           | Lỗi quản lý context          | 422         |
| `CSV_LOAD_ERROR`          | Lỗi load dữ liệu             | 500         |
| `INTERNAL_SERVER_ERROR`   | Lỗi server                   | 500         |

### Định Dạng Response Lỗi

```json
{
  "success": false,
  "error_code": "MÃ_LỖI",
  "error_message": "Thông báo lỗi thân thiện",
  "details": {
    "field": "tên_field",
    "value": "giá_trị_không_hợp_lệ",
    "constraint": "mô_tả_ràng_buộc"
  },
  "request_id": "uuid-string",
  "timestamp": "ISO-8601-timestamp"
}
```

### Best Practices

1. **Luôn kiểm tra `success`** trước khi xử lý response
2. **Log `request_id`** để debug
3. **Xử lý lỗi graceful** với thông báo thân thiện
4. **Retry lỗi 500** với exponential backoff

---

## 📝 Ví Dụ Chi Tiết

### Ví Dụ 1: Câu Hỏi Đơn Giản

**Request:**

```bash
curl -X POST http://localhost:8000/chat/advanced \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Học phí ngành Xây dựng?"
  }'
```

**Response:**

```json
{
  "analysis": {
    "intent": "hoi_hoc_phi",
    "score": 0.92,
    "entities": [
      {"label": "TEN_NGANH", "text": "xây dựng"}
    ]
  },
  "response": {
    "type": "tuition_info",
    "data": [
      {
        "major": "Xây dựng Dân dụng và Công nghiệp",
        "tuition_fee": "31,000,000 VNĐ/năm",
        "year": "2024"
      }
    ],
    "message": "Học phí ngành Xây dựng năm 2024"
  }
}
```

---

### Ví Dụ 2: Hội Thoại Liên Tục

**Request 1:**

```bash
curl -X POST http://localhost:8000/chat/advanced \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Điểm chuẩn ngành CNTT năm 2024?",
    "session_id": "conversation_1"
  }'
```

**Request 2 (Tiếp theo):**

```bash
curl -X POST http://localhost:8000/chat/advanced \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Còn học phí thế nào?",
    "session_id": "conversation_1"
  }'
```

> **Lưu ý:** Request thứ 2 không đề cập "CNTT" nhưng hệ thống dùng context để hiểu đang hỏi về cùng ngành.

---

### Ví Dụ 3: Xử Lý Lỗi

**Request (Message rỗng):**

```bash
curl -X POST http://localhost:8000/chat/advanced \
  -H "Content-Type: application/json" \
  -d '{
    "message": ""
  }'
```

**Response:**

```json
{
  "success": false,
  "error_code": "VALIDATION_ERROR",
  "error_message": "Câu hỏi không được để trống",
  "details": {
    "field": "message",
    "constraint": "min_length=1"
  },
  "request_id": "f3d4e5f6-...",
  "timestamp": "2025-11-25T14:30:00Z"
}
```

---

## 🔗 Tài Nguyên Liên Quan

- [Kiến Trúc Hệ Thống](./ARCHITECTURE.md)
- [Hướng Dẫn Testing](./TESTING_GUIDE.md)
- [Hướng Dẫn Contributing](./CONTRIBUTING.md)
- [Hướng Dẫn Deployment](./DEPLOYMENT.md)

---

## 📞 Hỗ Trợ

Nếu có vấn đề hoặc câu hỏi:

- **GitHub Issues:** [Link to repo]
- **Email:** support@huce-chatbot.com
- **Swagger UI:** http://localhost:8000/docs

---

## 🧪 Kiểm Thử & Chất Lượng

- Backend được kiểm tra bằng `pytest -q` (132 test) + `ruff check` + `mypy .`
- Trước khi gọi API từ client production, nên tự động gửi request smoke:
    1. `GET /`
    2. `POST /chat/advanced` với câu hỏi ngắn
    3. `POST /chat/context` với `reset` để chắc chắn context rỗng

---

**Cập nhật lần cuối:** 2025-11-25  
**Phiên bản API:** 1.0.0
