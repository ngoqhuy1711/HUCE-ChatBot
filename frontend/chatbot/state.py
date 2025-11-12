"""
State Management
================

File này quản lý state (trạng thái) của chatbot app.

State trong Reflex:
- Mỗi user có một state instance riêng (session-based)
- State được persist tự động giữa các page refresh
- Khi state thay đổi, UI tự động update (reactive)

ChatState chứa:
- messages: Danh sách tin nhắn trong cuộc hội thoại
- session_id: ID phiên (để backend nhận diện user)
- is_loading: Đang gửi request hay không
- error_message: Thông báo lỗi (nếu có)
"""

import reflex as rx
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
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
    """
    Model cho một tin nhắn trong chat.
    
    Attributes:
        role: "user" hoặc "bot"
        content: Nội dung tin nhắn (text)
        timestamp: Thời điểm gửi
        data: Dữ liệu bổ sung (optional) - dùng để hiển thị bảng, biểu đồ
              Có thể là Dict hoặc List tùy response từ backend
    
    Note: Dùng pydantic.BaseModel thay vì rx.Base (deprecated từ v0.8.15)
    """
    role: str  # "user" hoặc "bot"
    content: str  # Nội dung text
    timestamp: str  # ISO format timestamp
    data: Optional[Any] = None  # Dữ liệu bổ sung - có thể là Dict, List, hoặc Any


# ============================================================================
# CHAT STATE CLASS
# ============================================================================

class ChatState(rx.State):
    """
    State chính của chatbot app.
    
    State này tự động sync với UI - khi state thay đổi, UI update ngay.
    
    Attributes:
        messages: List tin nhắn trong cuộc hội thoại
        session_id: ID phiên duy nhất cho mỗi user
        is_loading: Đang xử lý request hay không
        error_message: Thông báo lỗi
        input_value: Giá trị hiện tại của input box
    
    Methods:
        send_message(): Gửi tin nhắn tới backend
        reset_conversation(): Reset hội thoại
        clear_error(): Xóa thông báo lỗi
    """
    
    # ========================================================================
    # STATE VARIABLES - Các biến state
    # ========================================================================
    
    # Danh sách tin nhắn
    messages: List[Message] = []
    
    # Session ID - Tạo unique ID cho mỗi user session
    # UUID4 đảm bảo ID không trùng lặp
    session_id: str = ""
    
    # Loading state
    is_loading: bool = False
    
    # Error handling
    error_message: str = ""
    
    # Input box value
    input_value: str = ""
    
    # Theme mode - "light" hoặc "dark"
    theme_mode: str = "light"
    
    # ========================================================================
    # LIFECYCLE METHODS
    # ========================================================================
    
    def on_load(self):
        """
        Được gọi khi page load lần đầu.
        
        Tạo session_id nếu chưa có.
        """
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
                        "• Điểm chuẩn, điểm sàn các ngành\n"
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
    # EVENT HANDLERS - Xử lý events từ UI
    # ========================================================================
    
    async def send_message(self):
        """
        Gửi tin nhắn từ user tới backend và nhận response.
        
        Luồng xử lý:
        1. Validate input
        2. Thêm tin nhắn user vào messages
        3. Gọi API backend
        4. Thêm response từ bot vào messages
        5. Clear input và error
        
        Được gọi khi user nhấn Enter hoặc click nút Send.
        """
        # Validate input
        if not self.input_value.strip():
            self.error_message = "Vui lòng nhập câu hỏi"
            return
        
        # Lưu input và clear input box ngay
        user_message = self.input_value.strip()
        self.input_value = ""
        self.error_message = ""
        
        # Thêm tin nhắn user vào chat
        self.messages.append(
            Message(
                role="user",
                content=user_message,
                timestamp=datetime.now().isoformat(),
            )
        )
        
        # Set loading state
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
                    data=bot_data,  # Dữ liệu bổ sung (nếu có)
                )
            )
            
            logger.info(f"Bot response: {bot_message[:100]}")
            
        except Exception as e:
            # Xử lý lỗi
            error_msg = f"Có lỗi xảy ra: {str(e)}"
            logger.error(error_msg)
            
            self.error_message = "Không thể kết nối tới server. Vui lòng thử lại sau."
            
            # Thêm error message vào chat
            self.messages.append(
                Message(
                    role="bot",
                    content="Xin lỗi, tôi gặp sự cố khi xử lý câu hỏi. Vui lòng thử lại.",
                    timestamp=datetime.now().isoformat(),
                )
            )
        
        finally:
            # Clear loading state
            self.is_loading = False
    
    async def reset_conversation(self):
        """
        Reset hội thoại - xóa tất cả messages và tạo session mới.
        
        Được gọi khi user click nút "Bắt đầu lại".
        """
        logger.info(f"Resetting conversation for session: {self.session_id}")
        
        try:
            # Reset context ở backend
            await backend_client.reset_context(session_id=self.session_id)
            
            # Tạo session ID mới
            self.session_id = str(uuid.uuid4())
            
            # Xóa tất cả messages
            self.messages = []
            
            # Clear input và error
            self.input_value = ""
            self.error_message = ""
            
            # Thêm welcome message mới
            self.messages.append(
                Message(
                    role="bot",
                    content=(
                        "Đã reset hội thoại! 🔄\n\n"
                        "Bạn có thể bắt đầu đặt câu hỏi mới."
                    ),
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
        """
        Xử lý khi user gõ vào input box.
        
        Args:
            value: Giá trị mới của input
        """
        self.input_value = value
        # Clear error khi user bắt đầu gõ
        if self.error_message:
            self.error_message = ""
    
    async def use_suggested_question(self, question: str):
        """
        Sử dụng câu hỏi gợi ý.
        
        Args:
            question: Câu hỏi được chọn
        """
        self.input_value = question
        await self.send_message()
    
    def toggle_theme(self):
        """
        Chuyển đổi giữa light mode và dark mode.
        """
        self.theme_mode = "dark" if self.theme_mode == "light" else "light"

