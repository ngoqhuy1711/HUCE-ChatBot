"""
Contact Module - Xử lý thông tin liên hệ
"""

import os
from typing import Any, Dict

from config import DATA_DIR
from .cache import read_csv


def get_contact_info() -> Dict[str, Any]:
    """
    Lấy thông tin liên hệ (hotline, email, fanpage)

    Returns:
        Dict chứa thông tin liên hệ
    """
    rows = read_csv(os.path.join(DATA_DIR, "contact_info.csv"))
    if rows:
        contact = rows[0]  # Chỉ có 1 row
        return {
            "university_name": contact.get("university_name", ""),
            "address": contact.get("address", ""),
            "email": contact.get("email", ""),
            "phone": contact.get("phone", ""),
            "hotline": contact.get("hotline", ""),
            "website": contact.get("website", ""),
            "fanpage": contact.get("fanpage", ""),
            "note": contact.get("note", "")
        }
    return {}
