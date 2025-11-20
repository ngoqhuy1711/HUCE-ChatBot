"""
State Management
================

File này quản lý state (trạng thái) của chatbot app.
"""

import reflex as rx
from pydantic import BaseModel
from typing import List, Any, Optional
import uuid
import logging
from datetime import datetime

from chatbot.api import backend_client

# Setup logger
logger = logging.getLogger(__name__)


# ============================================================================
# MESSAGE MODEL
# ============================================================================

class Message(BaseModel):
    """Model cho một tin nhắn trong chat."""
    role: str  # "user" hoặc "bot"
    content: str  # Nội dung text
    timestamp: str  # ISO format timestamp
    data: Optional[Any] = None  # Dữ liệu bổ sung


# ============================================================================
# CHAT STATE CLASS
# ============================================================================

class ChatState(rx.State):
    """State chính của chatbot app."""

    # State variables
    messages: List[Message] = []
    session_id: str = ""
    is_loading: bool = False
    error_message: str = ""
    input_value: str = ""
    theme_mode: str = "light"

    # ========================================================================
    # LIFECYCLE METHODS
    # ========================================================================

    def on_load(self):
        """Lifecycle hook - gọi khi page load."""
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
            logger.info(f"Created new session: {self.session_id}")

            # Thêm welcome message
            self.messages.append(
                Message(
                    role="bot",
                    content=(
                        "Xin chào! 👋 Tôi là chatbot tư vấn tuyển sinh Đại học Xây dựng Hà Nội.\n\n"
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

    # ========================================================================
    # EVENT HANDLERS
    # ========================================================================

    async def send_message(self):
        """Gửi tin nhắn từ user tới backend."""
        # Validate input
        if not self.input_value.strip():
            self.error_message = "Vui lòng nhập câu hỏi"
            return

        # Lưu và clear input
        user_message = self.input_value.strip()
        self.input_value = ""
        self.error_message = ""

        # Thêm tin nhắn user
        self.messages.append(
            Message(
                role="user",
                content=user_message,
                timestamp=datetime.now().isoformat(),
            )
        )

        # Set loading
        self.is_loading = True
        logger.info(f"User message: {user_message[:100]}")

        try:
            # Gọi backend API
            response = await backend_client.send_message(
                message=user_message,
                session_id=self.session_id,
                use_context=True,
            )

            # Parse response
            bot_response = response.get("response", {})
            bot_message = bot_response.get("message", "Xin lỗi, tôi không hiểu câu hỏi.")
            bot_data = bot_response.get("data", None)

            # Thêm response từ bot
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
            error_msg = f"Có lỗi xảy ra: {str(e)}"
            logger.error(error_msg)

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
            # Reset context ở backend
            await backend_client.reset_context(session_id=self.session_id)

            # Tạo session ID mới
            self.session_id = str(uuid.uuid4())

            # Xóa messages
            self.messages = []
            self.input_value = ""
            self.error_message = ""

            # Welcome message
            self.messages.append(
                Message(
                    role="bot",
                    content="Đã reset hội thoại! 🔄\n\nBạn có thể tra cứu thông tin tuyển sinh HUCE 2025.",
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
        """Xử lý khi user gõ vào input box."""
        self.input_value = value
        if self.error_message:
            self.error_message = ""

    async def use_suggested_question(self, question: str):
        """Sử dụng câu hỏi gợi ý."""
        self.input_value = question
        await self.send_message()

    def toggle_theme(self):
        """Toggle giữa light và dark mode."""
        self.theme_mode = "dark" if self.theme_mode == "light" else "light"
        logger.info(f"Theme switched to: {self.theme_mode}")

    def set_theme(self, theme: str):
        """Set theme mode."""
        if theme in ["light", "dark"]:
            self.theme_mode = theme
            logger.info(f"Theme set to: {theme}")

    def _detect_browser_theme(self):
        """Detect theme từ browser preference."""
        # Try to detect from browser using JavaScript
        # This will be executed on client-side
        try:
            # Check if we can use JavaScript to detect theme
            import reflex as rx
            # Use rx.call_script to detect theme preference
            dark_mode = rx.call_script(
                "(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches)"
            )
            if dark_mode:
                self.theme_mode = "dark"
                logger.info("Auto-detected dark theme from browser")
            else:
                self.theme_mode = "light"
                logger.info("Auto-detected light theme from browser")
        except:
            # Fallback to light theme
            self.theme_mode = "light"
            logger.info("Theme detection failed, using light theme")

