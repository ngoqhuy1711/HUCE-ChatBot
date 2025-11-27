"""State Management - Quản lý trạng thái của chatbot."""

import logging
import uuid
from datetime import datetime
from typing import List, Any, Optional

import reflex as rx
from chatbot.api import backend_client
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class Message(BaseModel):
    """Model cho một tin nhắn."""
    role: str  # "user" hoặc "bot"
    content: str
    timestamp: str
    data: Optional[Any] = None


class ChatState(rx.State):
    """State chính của chatbot."""

    messages: List[Message] = []
    session_id: str = ""
    is_loading: bool = False
    error_message: str = ""
    input_value: str = ""
    theme_mode: str = "light"

    def on_load(self):
        """Gọi khi page load."""
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
            logger.info(f"Created new session: {self.session_id}")
            self.detect_browser_theme()

            self.messages.append(
                Message(
                    role="bot",
                    content=(
                        "Xin chào! 👋 Tôi là trợ lý tra cứu thông tin tuyển sinh Đại học Xây dựng Hà Nội.\n\n"
                        "Bạn có thể hỏi tôi về:\n"
                        "• Điểm chuẩn các ngành\n"
                        "• Phương thức xét tuyển\n"
                        "• Học phí và học bổng\n"
                        "• Thông tin ngành học\n"
                        "• Lịch tuyển sinh\n\n"
                        "Hãy đặt câu hỏi của bạn! 😊"
                    ),
                    timestamp=datetime.now().isoformat(),
                )
            )

    def detect_browser_theme(self):
        """Đồng bộ theme với browser."""
        browser_window = getattr(rx, "window", None)
        if browser_window is None:
            return
        browser_window.match_media("(prefers-color-scheme: dark)").on_change(
            lambda e: self.set_theme("dark" if e.matches else "light")
        )
        browser_window.match_media("(prefers-color-scheme: dark)").mount(
            lambda e: self.set_theme("dark" if e.matches else "light")
        )

    async def send_message(self):
        """Gửi tin nhắn."""
        if not self.input_value.strip():
            self.error_message = "Vui lòng nhập câu hỏi"
            return

        user_message = self.input_value.strip()
        self.input_value = ""
        self.error_message = ""

        self.messages.append(
            Message(
                role="user",
                content=user_message,
                timestamp=datetime.now().isoformat(),
            )
        )

        self.is_loading = True
        logger.info(f"User message: {user_message[:100]}")

        try:
            response = await backend_client.send_message(
                message=user_message,
                session_id=self.session_id,
                use_context=True,
            )

            bot_response = response.get("response", {})
            bot_message = bot_response.get("message", "Xin lỗi, tôi không hiểu câu hỏi.")
            bot_data = bot_response.get("data", None)

            self.messages.append(
                Message(
                    role="bot",
                    content=bot_message,
                    timestamp=datetime.now().isoformat(),
                    data=bot_data,
                )
            )
            logger.info(f"Bot response: {bot_message[:100]}")

        except Exception as e:
            logger.error(f"Error: {str(e)}")
            self.error_message = "Không thể kết nối tới server. Vui lòng thử lại sau."
            self.messages.append(
                Message(
                    role="bot",
                    content="Xin lỗi, tôi gặp sự cố khi xử lý câu hỏi. Vui lòng thử lại.",
                    timestamp=datetime.now().isoformat(),
                )
            )

        finally:
            self.is_loading = False

    async def reset_conversation(self):
        """Reset hội thoại."""
        logger.info(f"Resetting conversation for session: {self.session_id}")

        try:
            await backend_client.reset_context(session_id=self.session_id)
            self.session_id = str(uuid.uuid4())
            self.messages = []
            self.input_value = ""
            self.error_message = ""

            self.messages.append(
                Message(
                    role="bot",
                    content="Đã reset hội thoại! 🔄\n\nBạn có thể tiếp tục tra cứu thông tin tuyển sinh HUCE 2025.",
                    timestamp=datetime.now().isoformat(),
                )
            )
            logger.info(f"Conversation reset - New session: {self.session_id}")

        except Exception as e:
            logger.error(f"Error resetting conversation: {str(e)}")
            self.error_message = "Có lỗi khi reset hội thoại"

    def clear_error(self):
        """Xóa thông báo lỗi."""
        self.error_message = ""

    def handle_input_change(self, value: str):
        """Xử lý khi user gõ."""
        self.input_value = value
        if self.error_message:
            self.error_message = ""

    def toggle_theme(self):
        """Toggle light/dark mode."""
        self.theme_mode = "dark" if self.theme_mode == "light" else "light"
        logger.info(f"Theme switched to: {self.theme_mode}")

    def set_theme(self, theme: str):
        """Set theme mode."""
        if theme in ["light", "dark"]:
            self.theme_mode = theme
            logger.info(f"Theme set to: {theme}")
