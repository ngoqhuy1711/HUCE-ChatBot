# HUCE Chatbot - Tư vấn Tuyển sinh

Hệ thống Chatbot tư vấn tuyển sinh Đại học Xây dựng Hà Nội.

## 📁 Cấu trúc dự án (Monorepo)

```
HUCE-ChatBot/
├── backend/          # Backend API (FastAPI + NLP)
├── frontend/         # Frontend (Reflex)
└── README.md         # File này
```

## 🚀 Hướng dẫn nhanh

### Backend

```bash
cd backend
uv sync
uv run uvicorn main:app --reload
```

Server: <http://localhost:8000>  
API Docs: <http://localhost:8000/docs>

Xem chi tiết: [backend/README.md](./backend/README.md)

### Frontend

```bash
cd frontend
uv sync
uv run reflex run
```

App: <http://localhost:8080>

Xem chi tiết: [frontend/README.md](./frontend/README.md)

## 🎯 Tính năng

- **NLP**: Nhận diện intent, trích xuất entity từ câu hỏi tiếng Việt
- **Tra cứu**: Ngành học, điểm chuẩn, học phí, học bổng (53 học bổng), phương thức tuyển sinh
- **Context**: Lưu ngữ cảnh hội thoại để hiểu câu hỏi tiếp theo
- **UI**: Giao diện chat đẹp, responsive với Reflex

## 🛠 Công nghệ

### Backend
- FastAPI (Python 3.13+)
- Underthesea (NLP tiếng Việt)
- TF-IDF + Cosine Similarity (Intent detection)
- CSV files (dễ cập nhật)

### Frontend
- Reflex (Python full-stack framework)
- HTTPX (API client)
- Responsive UI

## 📝 Lưu ý

- **Python version**: 3.10+ (frontend), 3.13+ (backend)
- **Package manager**: UV (khuyến nghị) hoặc pip
- **Encoding**: Tất cả files phải UTF-8
- **CORS**: Backend đã config sẵn cho frontend (port 8080)

## 📚 Tài liệu

- [Backend README](./backend/README.md)
- [Frontend README](./frontend/README.md)
- [API Documentation](http://localhost:8000/docs)

## 🤝 Contributing

1. Fork repository
2. Tạo branch mới: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -m "feat: add new feature"`
4. Push to branch: `git push origin feature/new-feature`
5. Tạo Pull Request

## 📄 License

Internal project - Đại học Xây dựng Hà Nội

---

**Phiên bản**: 1.0.0  
**Ngày cập nhật**: 2025-11-12  
**Trạng thái**: Production Ready ✅

