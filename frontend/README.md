# Chatbot Tuyển sinh HUCE - Frontend

Frontend của chatbot tư vấn tuyển sinh Đại học Xây dựng Hà Nội, xây dựng với **Reflex** (Python full-stack framework).

## 📋 Yêu cầu

- Python >= 3.10
- UV package manager (khuyến nghị) hoặc pip
- Backend API đang chạy tại `http://localhost:8000`

## 🚀 Cài đặt

### Với UV (Khuyến nghị - Nhanh hơn 10-100x):

```bash
# Cài UV (nếu chưa có)
# Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# Linux/Mac: curl -LsSf https://astral.sh/uv/install.sh | sh

cd frontend
uv venv                              # Tạo venv
uv pip install -r requirements.txt   # Cài packages
reflex init                          # Khởi tạo Reflex
```

### Hoặc với pip:

```bash
cd frontend
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
reflex init
```

## 🎯 Chạy ứng dụng

### Với UV (Cách dễ nhất):

```bash
cd frontend
uv run reflex run
```

### Hoặc activate venv trước:

```bash
# Activate
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Chạy
reflex run
```

App sẽ chạy tại: **http://localhost:8080**

### Production mode:

```bash
uv run reflex run --env prod
```

## 📁 Cấu trúc dự án

```
frontend/
├── rxconfig.py              # Reflex configuration
├── requirements.txt         # Python dependencies
├── README.md               # Documentation
├── .gitignore              # Git ignore rules
└── chatbot/                # Main app package
    ├── __init__.py         
    ├── chatbot.py          # Main app file (entry point)
    ├── state.py            # State management
    ├── api/                # API integration
    │   ├── __init__.py
    │   └── backend_client.py  # FastAPI client
    ├── components/         # UI components
    │   ├── __init__.py
    │   ├── chat_interface.py  # Main chat UI
    │   ├── message_bubble.py  # Message bubbles
    │   ├── input_box.py       # Input field + Send button
    │   └── suggested_questions.py  # Quick questions
    └── styles/             # Styling
        ├── __init__.py
        └── theme.py        # Colors, spacing, theme
```

## 🎨 Features

### Đã implement:
- ✅ Giao diện chat đẹp, responsive
- ✅ Gửi/nhận tin nhắn với backend
- ✅ Context management (lưu ngữ cảnh hội thoại)
- ✅ Loading states
- ✅ Error handling
- ✅ Câu hỏi gợi ý (quick questions)
- ✅ Reset hội thoại
- ✅ Auto-scroll to bottom
- ✅ Keyboard shortcuts (Enter to send)

### Chưa implement (TODO):
- ⏳ Hiển thị biểu đồ (charts) từ data
- ⏳ Hiển thị bảng dữ liệu (tables)
- ⏳ Export chat history
- ⏳ Dark mode
- ⏳ Mobile responsive improvements

## 🔧 Configuration

### Backend URL

Mặc định: `http://localhost:8000`

Để thay đổi, sửa trong `rxconfig.py`:

```python
config = rx.Config(
    backend_url="http://your-backend-url.com",
    ...
)
```

### Port

Mặc định: `8080`

Để thay đổi, sửa trong `rxconfig.py`:

```python
config = rx.Config(
    port=3000,  # Hoặc port khác
    ...
)
```

**Lưu ý:** Nếu đổi port, cần cập nhật CORS trong backend (`backend/config.py`).

## 📖 Cách sử dụng

### 1. User gửi tin nhắn:

- Gõ câu hỏi vào input box
- Nhấn **Enter** hoặc click **Gửi**
- Bot sẽ trả lời dựa trên backend NLP + data

### 2. Sử dụng câu hỏi gợi ý:

- Click vào một trong các câu hỏi gợi ý
- Câu hỏi sẽ tự động gửi đi

### 3. Reset hội thoại:

- Click nút **"Bắt đầu lại"** ở header
- Tất cả messages sẽ bị xóa
- Context sẽ được reset

## 🧪 Testing

### Test kết nối backend:

```bash
# Kiểm tra backend đang chạy
curl http://localhost:8000/

# Nếu thấy response: {"success": true, ...} → OK
```

### Test frontend:

1. Chạy frontend: `reflex run`
2. Mở browser: `http://localhost:8080`
3. Gửi thử câu hỏi: "Điểm chuẩn ngành Kiến trúc 2025"
4. Kiểm tra response có đúng không

## 🐛 Troubleshooting

### Lỗi: "Cannot connect to backend"

- Kiểm tra backend có đang chạy không: `curl http://localhost:8000/`
- Kiểm tra CORS: Backend phải allow `http://localhost:8080`
- Xem logs backend: `backend/logs/chatbot.log`

### Lỗi: "Module not found"

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Hoặc cài riêng Reflex
pip install reflex
```

### Lỗi: "Port already in use"

```bash
# Đổi port trong rxconfig.py
# Hoặc kill process đang dùng port 8080
```

## 📚 Tài liệu tham khảo

- [Reflex Documentation](https://reflex.dev/docs/)
- [Reflex Examples](https://reflex.dev/docs/examples/)
- [Backend API Documentation](../backend/README.md)
- [Business Requirements](./Business%20Req%20Doc.txt)

## 🤝 Contributing

Khi thêm features mới:

1. Tạo component mới trong `chatbot/components/`
2. Update state trong `chatbot/state.py` nếu cần
3. Import và sử dụng trong `chatbot/components/chat_interface.py`
4. Test kỹ trước khi commit
5. Comment đầy đủ bằng tiếng Việt

## 📝 License

Internal project - Đại học Xây dựng Hà Nội

