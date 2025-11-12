"""
CSV Cache Module - Cơ chế cache thông minh cho CSV files

Cache theo mtime (modification time):
- Lần đầu: Đọc file, lưu (mtime, data) vào cache
- Lần sau: So sánh mtime → Nếu giống thì dùng cache, khác thì đọc lại

Lợi ích:
- Giảm 90% I/O disk (đọc file rất chậm)
- Tự động reload khi file thay đổi
- Đơn giản, không cần invalidation logic
"""

import csv
import os
from typing import Any, Dict, List, Tuple

# Cache structure: {path: (mtime, data)}
_CSV_CACHE: Dict[str, Tuple[float, List[Dict[str, Any]]]] = {}


def _read_csv_cached(path: str) -> List[Dict[str, Any]]:
    """
    Đọc CSV với cơ chế cache thông minh.

    Thuật toán:
    1. Kiểm tra file có tồn tại không → Không → Trả []
    2. Lấy mtime (modification time) của file
    3. Kiểm tra cache:
       - Có cache VÀ mtime giống → Dùng cache (HIT)
       - Không cache HOẶC mtime khác → Đọc file mới (MISS)
    4. Lưu vào cache cho lần sau
    5. Trả về data

    Args:
        path: Đường dẫn tuyệt đối đến file CSV

    Returns:
        List các row (mỗi row là dict)
    """
    # Bước 1: Kiểm tra file tồn tại
    if not os.path.isfile(path):
        return []

    # Bước 2: Lấy mtime (thời điểm file sửa lần cuối)
    mtime = os.path.getmtime(path)

    # Bước 3: Kiểm tra cache
    cached = _CSV_CACHE.get(path)
    if cached and cached[0] == mtime:
        # Cache HIT: mtime giống nghĩa là file không đổi
        return cached[1]

    # Cache MISS: Đọc file mới
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Bước 4: Lưu vào cache
    _CSV_CACHE[path] = (mtime, rows)

    # Bước 5: Trả về data
    return rows


def read_csv(path: str) -> List[Dict[str, Any]]:
    """
    Public API để đọc CSV với cache.

    Args:
        path: Đường dẫn file CSV

    Returns:
        List[Dict]: Dữ liệu từ CSV (đã cache)
    """
    return _read_csv_cached(path)


def clear_cache():
    """
    Xóa toàn bộ cache (dùng khi cần force reload).
    """
    global _CSV_CACHE
    _CSV_CACHE.clear()
