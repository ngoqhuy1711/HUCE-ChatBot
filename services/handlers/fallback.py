"""
Fallback Handler - Xử lý các câu hỏi không nhận diện được intent
"""

from typing import Any, Dict

from services.processors import (
    list_majors,
    list_tuition,
    list_scholarships,
    add_contact_suggestion,
)

DEFAULT_GUIDE = "Nếu bạn cần thêm thông tin khác, cứ nói với mình nhé."


def _message_with_contact(*parts: str) -> str:
    content = "\n\n".join(p.strip() for p in parts if p and p.strip())
    return add_contact_suggestion(content)


def handle_fallback_query(message: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Xử lý câu hỏi khi không nhận diện được intent rõ ràng

    Args:
        message: Câu hỏi từ người dùng
        context: Context hội thoại hiện tại

    Returns:
        Response fallback (tất cả đều có gợi ý liên hệ)
    """
    message_lower = message.lower()

    # Tìm kiếm từ khóa chung
    if any(word in message_lower for word in ["ngành", "môn", "học"]):
        # Gợi ý tìm kiếm ngành
        results = list_majors()
        return {
            "type": "major_suggestions",
            "data": results[:10],  # Top 10 ngành
            "message": _message_with_contact(
                "Mình gửi bạn danh sách một số ngành học nổi bật của HUCE để tham khảo nhé.",
                DEFAULT_GUIDE,
            ),
        }

    elif any(word in message_lower for word in ["điểm", "chuẩn", "sàn"]):
        return {
            "type": "score_help",
            "message": _message_with_contact(
                'Bạn có thể hỏi về điểm chuẩn hoặc điểm sàn của từng ngành. '
                'Ví dụ: "Điểm chuẩn ngành Kiến trúc năm 2025" hoặc "Ngành CNTT lấy bao nhiêu điểm?"',
                DEFAULT_GUIDE,
            ),
        }

    elif any(word in message_lower for word in ["học phí", "tiền", "phí"]):
        results = list_tuition()
        return {
            "type": "tuition",
            "data": results,
            "message": _message_with_contact(
                "Đây là thông tin học phí mà mình tìm được.",
                DEFAULT_GUIDE,
            ),
        }

    elif any(word in message_lower for word in ["học bổng", "scholarship"]):
        results = list_scholarships()
        return {
            "type": "scholarships",
            "data": results,
            "message": _message_with_contact(
                "Mình gửi bạn danh sách các học bổng hiện có của trường.",
                DEFAULT_GUIDE,
            ),
        }

    else:
        return {
            "type": "general_help",
            "message": _message_with_contact(
                "Mình có thể hỗ trợ bạn tra cứu các thông tin như điểm chuẩn, ngành học, học phí, học bổng hoặc chỉ tiêu tuyển sinh.",
                "Bạn đang cần biết điều gì để mình hỗ trợ nhanh nhất?",
            ),
        }
