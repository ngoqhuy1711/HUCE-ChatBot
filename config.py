"""
Cấu hình lõi cho backend Chatbot Tư vấn Tuyển sinh HUCE.

==== MỤC ĐÍCH ====
Tập trung các hằng số/cấu hình và đọc từ environment variables:
- Dễ thay đổi tham số mà không cần sửa code
- Hỗ trợ nhiều môi trường (dev, staging, production)
- Tránh hardcode các giá trị nhạy cảm

==== CÁC THAM SỐ QUAN TRỌNG ====
1. DATA_DIR: Thư mục chứa tất cả file CSV/JSON
2. INTENT_THRESHOLD: Ngưỡng để chấp nhận một intent (0.0-1.0)
   - Càng cao: bot càng "chắc chắn" nhưng có thể bỏ sót
   - Càng thấp: nhận diện nhiều hơn nhưng dễ sai
   - Mặc định: 0.35 (kết quả thử nghiệm thực tế)
3. CONTEXT_HISTORY_LIMIT: Số câu lưu trong context
   - Mặc định: 10 câu
4. CORS_ORIGINS: Danh sách origins được phép truy cập API

==== CẤU HÌNH ====
Tạo file .env trong thư mục backend (copy từ env.example):
```bash
cp env.example .env
# Sau đó chỉnh sửa .env theo nhu cầu
```

==== SỬ DỤNG ====
```python
from config import DATA_DIR, get_intent_threshold, get_cors_origins

# Đọc file CSV
csv_path = os.path.join(DATA_DIR, "major_intro.csv")

# Lấy ngưỡng intent
threshold = get_intent_threshold()

# Lấy CORS origins
origins = get_cors_origins()
```
"""

import os
from typing import List

# ============================================================================
# ĐƯỜNG DẪN THƯ MỤC
# ============================================================================
# BASE_DIR: Thư mục gốc của backend (nơi chứa file này)
BASE_DIR = os.path.dirname(__file__)

# DATA_DIR: Thư mục chứa dữ liệu CSV/JSON
# Tất cả dữ liệu tuyển sinh nằm ở đây
DATA_DIR = os.path.join(BASE_DIR, "data")

# ============================================================================
# THAM SỐ MẶC ĐỊNH
# ============================================================================

# NLP
INTENT_THRESHOLD_DEFAULT: float = 0.25  # Giảm từ 0.35 xuống 0.25 để nhận diện tốt hơn
CONTEXT_HISTORY_LIMIT_DEFAULT: int = 10

# Server
SERVER_HOST_DEFAULT: str = "0.0.0.0"
SERVER_PORT_DEFAULT: int = 8000
DEBUG_DEFAULT: bool = False
LOG_LEVEL_DEFAULT: str = "INFO"

# CORS
CORS_ORIGINS_DEFAULT: List[str] = [
    "http://localhost:3000",  # Reflex frontend
    "http://localhost:8001",  # Reflex backend (WebSocket)
    "http://localhost:5173",  # Vite
    "http://localhost:8080",  # Fallback
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8001",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8080",
]
CORS_ALLOW_CREDENTIALS_DEFAULT: bool = True

# API
MAX_RESULTS_DEFAULT: int = 100
MAX_SUGGESTIONS_DEFAULT: int = 20


# ============================================================================
# GETTER FUNCTIONS - Hàm lấy cấu hình từ environment
# ============================================================================


def get_intent_threshold() -> float:
    """
    Lấy ngưỡng nhận diện intent từ environment hoặc mặc định.

    Returns:
        float: Ngưỡng confidence (0-1), mặc định 0.35
    """
    return float(os.getenv("INTENT_THRESHOLD", INTENT_THRESHOLD_DEFAULT))


def get_context_history_limit() -> int:
    """
    Lấy giới hạn độ dài lịch sử hội thoại từ environment hoặc mặc định.

    Returns:
        int: Số câu hỏi tối đa được lưu, mặc định 10
    """
    return int(os.getenv("CONTEXT_HISTORY_LIMIT", CONTEXT_HISTORY_LIMIT_DEFAULT))


def get_server_host() -> str:
    """
    Lấy host cho server từ environment hoặc mặc định.

    Returns:
        str: Host, mặc định "0.0.0.0"
    """
    return os.getenv("SERVER_HOST", SERVER_HOST_DEFAULT)


def get_server_port() -> int:
    """
    Lấy port cho server từ environment hoặc mặc định.

    Returns:
        int: Port, mặc định 8000
    """
    return int(os.getenv("SERVER_PORT", SERVER_PORT_DEFAULT))


def get_debug_mode() -> bool:
    """
    Lấy debug mode từ environment hoặc mặc định.

    Returns:
        bool: Debug mode, mặc định False
    """
    debug_str = os.getenv("DEBUG", str(DEBUG_DEFAULT)).lower()
    return debug_str in ("true", "1", "yes", "on")


def get_log_level() -> str:
    """
    Lấy log level từ environment hoặc mặc định.

    Returns:
        str: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL), mặc định INFO
    """
    return os.getenv("LOG_LEVEL", LOG_LEVEL_DEFAULT).upper()


def get_cors_origins() -> List[str]:
    """
    Lấy danh sách CORS origins từ environment hoặc mặc định.

    Environment variable CORS_ORIGINS format: "http://localhost:3000,http://localhost:5173"

    Returns:
        List[str]: Danh sách origins được phép
    """
    origins_str = os.getenv("CORS_ORIGINS", None)
    if origins_str:
        # Parse từ string ngăn cách bởi dấu phẩy
        return [origin.strip() for origin in origins_str.split(",") if origin.strip()]
    return CORS_ORIGINS_DEFAULT


def get_cors_allow_credentials() -> bool:
    """
    Lấy CORS allow credentials từ environment hoặc mặc định.

    Returns:
        bool: Allow credentials, mặc định True
    """
    allow_str = os.getenv(
        "CORS_ALLOW_CREDENTIALS", str(CORS_ALLOW_CREDENTIALS_DEFAULT)
    ).lower()
    return allow_str in ("true", "1", "yes", "on")


def get_max_results() -> int:
    """
    Lấy số kết quả tối đa từ environment hoặc mặc định.

    Returns:
        int: Số kết quả tối đa, mặc định 100
    """
    return int(os.getenv("MAX_RESULTS", MAX_RESULTS_DEFAULT))


def get_max_suggestions() -> int:
    """
    Lấy số gợi ý ngành tối đa từ environment hoặc mặc định.

    Returns:
        int: Số gợi ý tối đa, mặc định 20
    """
    return int(os.getenv("MAX_SUGGESTIONS", MAX_SUGGESTIONS_DEFAULT))
