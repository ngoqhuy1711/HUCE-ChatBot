"""
Components Package
==================

Chứa tất cả UI components của chatbot.

Components:
- chat_interface: Component chính chứa toàn bộ giao diện chat
- message_bubble: Bubble hiển thị từng tin nhắn
- input_box: Ô nhập câu hỏi + nút gửi
- suggested_questions: Danh sách câu hỏi gợi ý
"""

from .chat_interface import chat_interface
from .message_bubble import message_bubble
from .input_box import input_box
from .suggested_questions import suggested_questions

__all__ = [
    "chat_interface",
    "message_bubble",
    "input_box",
    "suggested_questions",
]

