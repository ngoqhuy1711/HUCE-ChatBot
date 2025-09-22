# Chatbot Tư vấn Tuyển sinh HUCE (Dự án cá nhân)

Backend FastAPI + NLP tiếng Việt (Underthesea) để trả lời câu hỏi tuyển sinh HUCE từ dữ liệu CSV đã chuẩn hóa.

## Công nghệ

- Backend: FastAPI (Python)
- NLP: Underthesea, đối sánh intent TF‑IDF cosine, entity theo rule
- Dữ liệu: CSV/JSON trong `backend/data`

## Cấu trúc thư mục

- `backend/main.py`: Ứng dụng FastAPI, endpoint `POST /chat`
- `backend/nlu/pipeline.py`: Pipeline NLP (tiền xử lý, synonyms, intent, entity)
- `backend/data/`: Bộ dữ liệu chuẩn (source of truth)
- `Business Req Doc.txt`: Tài liệu nghiệp vụ và kế hoạch tuần

## Cài đặt

Yêu cầu Python 3.10+

```bash
pip install -r requirements.txt
```

## Chạy server

```bash
uvicorn backend.main:app --reload
```

## API

- Health: `GET /` → `{ "message": "OK" }`
- Chat: `POST /chat`
    - Body ví dụ:
      ```json
      { "message": "Điểm chuẩn ngành Kỹ thuật xây dựng 2025" }
      ```
    - Response ví dụ:
      ```json
      { "intent": "hoi_diem_chuan", "score": 0.45, "entities": [{"label":"MA_NGANH","text":"7580201"}] }
      ```

## Dữ liệu

- Chỉ sử dụng thư mục `backend/data` làm dữ liệu chuẩn.
- File chính:
    - `intent.csv`: mẫu câu (utterance,intent) dùng nhận diện intent
    - `entity.json`: rule nhãn cho entity
    - `standard_score.csv`, `floor_score.csv`, `admission_quota.csv`, ...
    - `synonym.csv`: ánh xạ từ đồng nghĩa/viết tắt

## NLP

- Tiền xử lý: lowercase, chuẩn hóa Unicode, loại ký tự đặc biệt, tách từ (Underthesea)
- Synonyms: ánh xạ theo token từ `synonym.csv`
- Intent: TF‑IDF cosine so với trọng tâm (centroid) của từng intent; ngưỡng mặc định: 0.35; ưu tiên intent bắt đầu
  `hoi_`
- Entity: match theo chuỗi con từ `entity.json`

## Lộ trình tiếp theo

- Viết hàm trả lời dựa trên CSV cho từng intent (điểm chuẩn, điểm sàn, chỉ tiêu, học phí, phương thức)
- Mở rộng rule entity và bộ kiểm thử
- Frontend chat (React + Tailwind) và biểu đồ thống kê
