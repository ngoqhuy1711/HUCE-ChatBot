# Kiến Trúc Hệ Thống - HUCE Chatbot

**Phiên bản:** 1.0.0  
**Cập nhật:** 2025-11-25

---

## 📚 Mục Lục

1. [Tổng Quan](#tổng-quan)
2. [Sơ Đồ Kiến Trúc](#sơ-đồ-kiến-trúc)
3. [Các Thành Phần](#các-thành-phần)
4. [Luồng Dữ Liệu](#luồng-dữ-liệu)
5. [Design Patterns](#design-patterns)
6. [Tech Stack](#tech-stack)
7. [Bảo Mật](#bảo-mật)
8. [Hiệu Năng](#hiệu-năng)

---

## 📖 Tổng Quan

HUCE Chatbot là ứng dụng full-stack cung cấp tư vấn tuyển sinh thông minh thông qua:

- **NLP** cho hiểu ngôn ngữ tiếng Việt
- **Context Management** cho hội thoại nhiều lượt
- **Data Integration** với cơ sở dữ liệu tuyển sinh
- **Real-time Frontend** cho tương tác người dùng

### Đặc Điểm Chính

- **API Stateless:** Mỗi request độc lập (context lưu riêng)
- **Thiết kế Modular:** Phân tách rõ ràng các concerns
- **Test-Driven:** 132 tests với 80% coverage
- **Production-Ready:** Xử lý lỗi toàn diện

---

## 🏗 Sơ Đồ Kiến Trúc

### Kiến Trúc Tổng Quan

```
┌─────────────┐
│   Client    │  (Web Browser)
│  (Reflex)   │
└──────┬──────┘
       │ HTTP/WebSocket
       ▼
┌─────────────────────────────────────┐
│         FastAPI Backend             │
│  ┌───────────────────────────────┐  │
│  │     API Endpoints             │  │
│  │  - /chat/advanced             │  │
│  │  - /chat/context              │  │
│  │  - /                          │  │
│  └──────────┬────────────────────┘  │
│             ▼                        │
│  ┌───────────────────────────────┐  │
│  │    Middleware Layer           │  │
│  │  - Request ID                 │  │
│  │  - CORS                       │  │
│  │  - Exception Handling         │  │
│  └──────────┬────────────────────┘  │
│             ▼                        │
│  ┌───────────────────────────────┐  │
│  │    Services Layer             │  │
│  │  - NLP Service                │  │
│  │  - CSV Service                │  │
│  │  - Context Management         │  │
│  └──────────┬────────────────────┘  │
│             ▼                        │
│  ┌───────────────────────────────┐  │
│  │    NLU Layer                  │  │
│  │  - Phát hiện Intent           │  │
│  │  - Trích xuất Entity          │  │
│  │  - Tiền xử lý Text            │  │
│  └──────────┬────────────────────┘  │
│             ▼                        │
│  ┌───────────────────────────────┐  │
│  │    Data Layer                 │  │
│  │  - CSV Files                  │  │
│  │  - Data Processors            │  │
│  │  - Cache                      │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

### Luồng Request

```
1. User Input → Frontend (Reflex)
         ↓
2. HTTP POST → FastAPI Endpoint
         ↓
3. Request ID Middleware → Gán ID duy nhất
         ↓
4. Validation → Pydantic models
         ↓
5. NLP Service → Phân tích message
         ↓
6. Intent Detection → TF-IDF + Cosine Similarity
         ↓
7. Entity Extraction → Regex + Dictionary + NER
         ↓
8. Context Management → Merge với context trước
         ↓
9. Data Retrieval → CSV processors với cache
         ↓
10. Response Formation → Cấu trúc data + message
         ↓
11. Context Update → Lưu cho lượt tiếp
         ↓
12. JSON Response → Trả về client
         ↓
13. Frontend Update → Hiển thị cho user
```

---

## 🧩 Các Thành Phần

### 1. API Layer (`main.py`)

**Nhiệm vụ:**

- Xử lý HTTP requests
- Route đến handlers thích hợp
- Exception handling
- Request/response validation

**Tính năng chính:**

- Request ID middleware
- CORS configuration
- Exception handlers (3 loại)
- Swagger documentation

---

### 2. Services Layer

#### NLP Service (`services/nlp_service.py`)

**Nhiệm vụ:**

- Điều phối NLP pipeline
- Quản lý context store
- Phối hợp intent handling

**Design Pattern:** Facade Pattern

```python
class NLPService:
    def __init__(self):
        self.pipeline = NLPPipeline()
        self.context_store = {}

    def handle_message(self, message, context):
        # Phân tích với NLP
        analysis = self.pipeline.analyze(message)

        # Xử lý intent
        response = handle_intent(analysis, context)

        return {"analysis": analysis, "response": response}
```

#### CSV Service (`services/csv_service.py`)

**Nhiệm vụ:**

- Load CSV data với caching
- Cung cấp interface truy cập data

**Design Pattern:** Singleton + Cache Pattern

---

### 3. NLU Layer

#### Pipeline (`nlu/pipeline.py`)

Phối hợp các components NLP

#### Intent Detection (`nlu/intent.py`)

**Thuật toán:** TF-IDF + Cosine Similarity

```python
# 1. Load dữ liệu training intent
intents = load_intent_data()

# 2. Build TF-IDF vectorizer
vectorizer = TfidfVectorizer()
intent_vectors = vectorizer.fit_transform(intent_texts)

# 3. Với message mới
message_vector = vectorizer.transform([message])
similarities = cosine_similarity(message_vector, intent_vectors)

# 4. Trả về best match
best_intent = intents[np.argmax(similarities)]
```

#### Entity Extraction (`nlu/entities.py`)

**Chiến lược đa dạng:**

1. **Pattern Matching** (Regex)
   ```python
   PATTERNS = {
       "NAM_HOC": r"\b(20\d{2})\b",
       "TO_HOP": r"\b([A-D]\d{2})\b"
   }
   ```

2. **Dictionary Lookup**
   ```python
   MAJOR_DICT = {"cntt": "Công nghệ Thông tin", ...}
   ```

3. **Named Entity Recognition** (Underthesea)

---

### 4. Data Layer

#### Nguồn Dữ Liệu

```
data/
├── admission_scores.csv      # Điểm chuẩn
├── majors.csv                # Danh sách ngành
├── tuition.csv               # Học phí
├── scholarships.csv          # Học bổng
├── admission_methods.csv     # Phương thức xét tuyển
└── ...
```

#### Data Processors

```python
def find_standard_score(major=None, year=None):
    # 1. Load data với cache
    data = get_cached_data("admission_scores.csv")
    
    # 2. Lọc theo tham số
    if major:
        data = filter_by_major(data, major)
    if year:
        data = filter_by_year(data, year)
    
    # 3. Format và trả về
    return format_data(data)
```

---

### 5. Exception Layer

**Hierarchy:**

```
ChatbotException (base)
├── NLPException
│   ├── IntentNotFoundError
│   ├── EntityExtractionError
│   ├── ContextError
│   └── PreprocessingError
├── DataException
│   ├── DataNotFoundError
│   ├── CSVLoadError
│   ├── InvalidMajorError
│   └── DataValidationError
└── APIException
    ├── ValidationError
    ├── RateLimitError
    ├── AuthenticationError
    └── ResourceNotFoundError
```

---

## 🔄 Luồng Dữ Liệu

### Ví Dụ: Truy Vấn Điểm Chuẩn

```
1. User: "Điểm chuẩn ngành Kiến trúc?"
         ↓
2. Frontend gửi POST đến /chat/advanced
         ↓
3. Request ID: abc-123 được gán
         ↓
4. Sanitize input: Kiểm tra XSS, giới hạn độ dài
         ↓
5. Lấy context: Kiểm tra có tiếp tục không
         ↓
6. Phân tích NLP:
   - Intent: "hoi_diem_chuan" (score: 0.95)
   - Entities: [{"label": "TEN_NGANH", "text": "kiến trúc"}]
         ↓
7. Lấy Dữ Liệu:
   - Load admission_scores.csv (cached)
   - Lọc theo major="Kiến trúc"
   - Format kết quả
         ↓
8. Tạo Response:
   {
     "type": "standard_score",
     "data": [...],
     "message": "Điểm chuẩn ngành Kiến trúc năm 2024"
   }
         ↓
9. Cập Nhật Context:
   - Lưu last_intent
   - Lưu last_entities
   - Thêm vào conversation_history
         ↓
10. Trả Response với Request ID
         ↓
11. Frontend hiển thị kết quả
```

---

## 🎨 Design Patterns

### 1. Facade Pattern

**Dùng trong:** `NLPService`  
**Mục đích:** Đơn giản hóa NLP subsystem phức tạp

### 2. Singleton Pattern

**Dùng trong:** `CSVDataService`, `NLPService`  
**Mục đích:** Single instance cho data/service

### 3. Strategy Pattern

**Dùng trong:** Entity Extraction  
**Mục đích:** Nhiều chiến lược trích xuất

### 4. Cache Pattern

**Dùng trong:** CSV Data Loading  
**Mục đích:** Tránh đọc file lặp lại

```python
def get_cached_data(filename):
    cache_key = filename
    mtime = os.path.getmtime(filename)
    
    if cache_key in CACHE and CACHE[cache_key]["mtime"] == mtime:
        return CACHE[cache_key]["data"]
    
    data = load_csv(filename)
    CACHE[cache_key] = {"data": data, "mtime": mtime}
    return data
```

---

## 💻 Tech Stack

### Backend

| Component      | Technology      | Mục Đích                  |
|----------------|-----------------|---------------------------|
| **Framework**  | FastAPI 0.121.2 | Web framework             |
| **NLP**        | Underthesea     | Vietnamese NLP            |
| **ML**         | scikit-learn    | TF-IDF, Cosine Similarity |
| **Validation** | Pydantic        | Request/response models   |
| **Testing**    | pytest          | Test framework            |
| **Data**       | pandas          | Xử lý CSV                 |

### Frontend

| Component         | Technology   | Mục Đích             |
|-------------------|--------------|----------------------|
| **Framework**     | Reflex       | Python web framework |
| **State**         | Reflex State | Quản lý state        |
| **Communication** | WebSocket    | Cập nhật realtime    |

---

## 🔒 Bảo Mật

### Làm Sạch Input

```python
# Ngăn XSS
message = html.escape(message)

# Ngăn SQL Injection
dangerous_patterns = [
    r';\s*(DROP|DELETE|UPDATE)',
    r'(UNION|SELECT).*FROM'
]
for pattern in dangerous_patterns:
    message = re.sub(pattern, '', message)

# Giới hạn độ dài
if len(message) > 1000:
    message = message[:1000]
```

### Xử Lý Lỗi

- **Không expose stack traces** trong production
- **Request IDs** để debug an toàn
- **Error messages được sanitize** cho users

### Bảo Vệ Dữ Liệu

- **Không lưu user data** (stateless)
- **Session IDs** được validate và sanitize
- **CORS** được cấu hình cho allowed origins

---

## ⚡ Hiệu Năng

### Response Time

```
Average: <200ms
P95:     <300ms
P99:     <500ms
```

### Chiến Lược Tối Ưu

1. **Caching**
    - CSV data cached trong memory
    - Cache invalidation khi file thay đổi (mtime)

2. **Vectorization**
    - TF-IDF vectors được tính trước
    - Batch cosine similarity

3. **Lazy Loading**
    - Models load khi dùng lần đầu
    - Data load on demand

### Khả Năng Mở Rộng

**Capacity Hiện Tại:**

- 50+ concurrent users
- ~100MB memory usage
- Single instance xử lý tốt

**Chiến Lược Scaling:**

- **Horizontal:** Nhiều FastAPI instances sau load balancer
- **Vertical:** Tăng instance size cho nhiều memory hơn
- **Caching:** Redis cho distributed cache

---

## 📊 Monitoring

### Logging

```python
# Structured logging với Request ID
logger.info(
    "[%s] Intent: %s (score: %.2f)",
    request_id, intent, score
)
```

### Metrics Cần Track

- Request count theo endpoint
- Response times (P50, P95, P99)
- Error rates theo loại
- Phân bố intent
- Cache hit rate

---

## 🔮 Cải Tiến Tương Lai

### Ngắn Hạn

1. **Rate Limiting** - Ngăn abuse
2. **Authentication** - API key support
3. **Monitoring Dashboard** - Real-time metrics

### Dài Hạn

1. **Machine Learning**
    - Train custom NER model
    - Cải thiện intent detection
    - Personalized responses

2. **Database Integration**
    - Thay CSV bằng PostgreSQL
    - Quản lý data tốt hơn

3. **Microservices**
    - Tách NLP service
    - Tách data service
    - Independent scaling

---

**Cập nhật lần cuối:** 2025-11-25  
**Phiên bản:** 1.0.0

