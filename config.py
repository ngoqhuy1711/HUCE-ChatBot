"""
Cấu hình lõi cho backend Chatbot Tư vấn Tuyển sinh HUCE.

==== MỤC ĐÍCH ====
Tập trung các hằng số/cấu hình để:
- Dễ thay đổi tham số mà không cần sửa nhiều file
- Dễ chuyển sang đọc từ biến môi trường sau này (ENV variables)
- Tránh "magic numbers" nằm rải rác trong code

==== CÁC THAM SỐ QUAN TRỌNG ====
1. DATA_DIR: Thư mục chứa tất cả file CSV/JSON
2. INTENT_THRESHOLD_DEFAULT: Ngưỡng để chấp nhận một intent
   - Càng cao: chatbot càng "chắc chắn" nhưng có thể bỏ sót
   - Càng thấp: nhận diện nhiều hơn nhưng dễ sai
   - Giá trị 0.35 là kết quả thử nghiệm thực tế
3. CONTEXT_HISTORY_LIMIT: Số câu hỏi gần nhất được lưu trong context
   - 10 câu = đủ để chatbot "nhớ" cuộc hội thoại
   - Tránh lưu quá nhiều gây tốn bộ nhớ

==== SỬ DỤNG ====
```python
from config import DATA_DIR, get_intent_threshold

# Đọc file CSV
csv_path = os.path.join(DATA_DIR, "major_intro.csv")

# Lấy ngưỡng intent
threshold = get_intent_threshold()
```
"""

import os

# ============================================================================
# ĐƯỜNG DẪN THƯ MỤC
# ============================================================================
# BASE_DIR: Thư mục gốc của backend (nơi chứa file này)
BASE_DIR = os.path.dirname(__file__)

# DATA_DIR: Thư mục chứa dữ liệu CSV/JSON
# Tất cả dữ liệu tuyển sinh nằm ở đây
DATA_DIR = os.path.join(BASE_DIR, "data")


# ============================================================================
# THAM SỐ NLP VÀ HỘI THOẠI
# ============================================================================

# Ngưỡng nhận diện intent (confidence threshold)
# Intent có score >= 0.35 sẽ được chấp nhận
# Intent có score < 0.35 sẽ rơi vào fallback (tìm kiếm theo từ khóa)
INTENT_THRESHOLD_DEFAULT: float = 0.35

# Giới hạn độ dài lịch sử hội thoại
# Chỉ giữ 10 câu hỏi-trả lời gần nhất trong context
# Tránh context quá dài gây tốn bộ nhớ và chậm xử lý
CONTEXT_HISTORY_LIMIT: int = 10


# ============================================================================
# GETTER FUNCTIONS - Hàm lấy cấu hình
# ============================================================================
# Thiết kế như hàm để sau này dễ mở rộng đọc từ biến môi trường

def get_intent_threshold() -> float:
    """
    Trả về ngưỡng nhận diện intent.
    
    Sau này có thể mở rộng thành:
    ```python
    return float(os.getenv("INTENT_THRESHOLD", INTENT_THRESHOLD_DEFAULT))
    ```
    
    Returns:
        float: Ngưỡng confidence (0-1), mặc định 0.35
    """
    return INTENT_THRESHOLD_DEFAULT


def get_context_history_limit() -> int:
    """
    Trả về giới hạn độ dài lịch sử hội thoại.
    
    Returns:
        int: Số câu hỏi tối đa được lưu, mặc định 10
    """
    return CONTEXT_HISTORY_LIMIT
