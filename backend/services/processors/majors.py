"""
Majors Module - Xử lý thông tin ngành học
"""

import os
from typing import Any, Dict, List, Optional

from config import DATA_DIR
from .cache import read_csv
from .utils import strip_diacritics


def list_majors(query: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Tìm kiếm thông tin ngành học (lọc theo tên/mã ngành nếu có)

    Args:
        query: Từ khóa tìm kiếm (tên ngành hoặc mã ngành)

    Returns:
        List các ngành học phù hợp
    """
    rows = read_csv(os.path.join(DATA_DIR, "majors.csv"))

    # Lọc theo từ khóa nếu có
    if query:
        q = query.lower()
        q_ascii = strip_diacritics(q)
        rows = [
            r
            for r in rows
            if q in (r.get("major_name") or "").lower()
               or q in (r.get("major_code") or "").lower()
               or q_ascii in strip_diacritics((r.get("major_name") or "").lower())
        ]

    # Trả về format chuẩn
    return [
        {
            "major_code": r.get("major_code"),
            "major_name": r.get("major_name"),
            "description": r.get("description"),
            "additional_info": r.get("additional_info"),
        }
        for r in rows
    ]
