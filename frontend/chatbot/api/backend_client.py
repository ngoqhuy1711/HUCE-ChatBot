"""
Backend API Client
==================

Client để gọi các API endpoints của FastAPI backend.

Usage:
    from chatbot.api import backend_client
    
    # Gửi tin nhắn
    response = await backend_client.send_message("Điểm chuẩn ngành Kiến trúc")
    
    # Reset context
    await backend_client.reset_context(session_id="user_123")
"""

import httpx
from typing import Dict, Any, Optional, List
import logging

# Setup logger
logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTS - Các hằng số API
# ============================================================================

# Base URL của FastAPI backend
# Trong production, lấy từ environment variable
BACKEND_URL = "http://localhost:8000"

# Timeout cho API calls (giây)
TIMEOUT = 30.0

# Default headers
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}


# ============================================================================
# BACKEND CLIENT CLASS
# ============================================================================

class BackendClient:
    """
    Client để tương tác với FastAPI backend.
    
    Attributes:
        base_url: URL gốc của backend
        timeout: Timeout cho mỗi request
        client: httpx.AsyncClient instance
    
    Methods:
        send_message(): Gửi tin nhắn và nhận response
        reset_context(): Reset context hội thoại
        get_majors(): Lấy danh sách ngành
        suggest_majors(): Gợi ý ngành theo điểm
        get_scholarships(): Lấy thông tin học bổng
    """
    
    def __init__(self, base_url: str = BACKEND_URL, timeout: float = TIMEOUT):
        """
        Khởi tạo client.
        
        Args:
            base_url: URL của backend API
            timeout: Timeout (giây)
        """
        self.base_url = base_url.rstrip("/")  # Bỏ dấu / cuối nếu có
        self.timeout = timeout
        self.client: Optional[httpx.AsyncClient] = None
        
        logger.info(f"Backend client initialized with base_url: {self.base_url}")
    
    async def _get_client(self) -> httpx.AsyncClient:
        """
        Lấy hoặc tạo httpx client.
        
        Lazy initialization: Chỉ tạo client khi cần dùng.
        
        Returns:
            httpx.AsyncClient instance
        """
        if self.client is None:
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers=DEFAULT_HEADERS,
            )
            logger.debug("Created new httpx.AsyncClient")
        return self.client
    
    async def close(self):
        """Đóng client khi không dùng nữa."""
        if self.client is not None:
            await self.client.aclose()
            self.client = None
            logger.debug("Closed httpx.AsyncClient")
    
    # ========================================================================
    # CHAT ENDPOINTS
    # ========================================================================
    
    async def send_message(
        self,
        message: str,
        session_id: str = "default",
        use_context: bool = True,
    ) -> Dict[str, Any]:
        """
        Gửi tin nhắn tới backend và nhận response.
        
        Endpoint: POST /chat/advanced
        
        Args:
            message: Câu hỏi từ user
            session_id: ID phiên hội thoại (để lưu context)
            use_context: Có sử dụng context hay không
        
        Returns:
            Dict chứa:
            - analysis: Kết quả phân tích NLP
            - response: Response từ bot
            - context: Context mới sau khi xử lý
        
        Raises:
            httpx.HTTPError: Nếu request thất bại
        """
        client = await self._get_client()
        
        payload = {
            "message": message,
            "session_id": session_id,
            "use_context": use_context,
        }
        
        logger.info(f"Sending message to /chat/advanced - Session: {session_id}")
        
        try:
            response = await client.post("/chat/advanced", json=payload)
            response.raise_for_status()  # Raise exception nếu status code không OK
            
            data = response.json()
            logger.info(f"Received response - Intent: {data.get('analysis', {}).get('intent')}")
            
            return data
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error when sending message: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error when sending message: {str(e)}")
            raise
    
    async def reset_context(self, session_id: str = "default") -> Dict[str, Any]:
        """
        Reset context hội thoại (bắt đầu lại từ đầu).
        
        Endpoint: POST /chat/context
        
        Args:
            session_id: ID phiên cần reset
        
        Returns:
            Dict với success message
        """
        client = await self._get_client()
        
        payload = {
            "action": "reset",
            "session_id": session_id,
        }
        
        logger.info(f"Resetting context for session: {session_id}")
        
        try:
            response = await client.post("/chat/context", json=payload)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Context reset successfully")
            
            return data
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error when resetting context: {str(e)}")
            raise
    
    # ========================================================================
    # DATA ENDPOINTS
    # ========================================================================
    
    async def get_majors(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lấy danh sách ngành học.
        
        Endpoint: GET /nganh
        
        Args:
            query: Từ khóa tìm kiếm (optional)
        
        Returns:
            List các ngành học
        """
        client = await self._get_client()
        
        params = {}
        if query:
            params["q"] = query
        
        logger.info(f"Fetching majors with query: {query}")
        
        try:
            response = await client.get("/nganh", params=params)
            response.raise_for_status()
            
            data = response.json()
            items = data.get("items", [])
            logger.info(f"Fetched {len(items)} majors")
            
            return items
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error when fetching majors: {str(e)}")
            return []
    
    async def suggest_majors(
        self,
        score: float,
        score_type: str = "chuan",
        year: str = "2025",
    ) -> Dict[str, Any]:
        """
        Gợi ý ngành theo điểm số.
        
        Endpoint: POST /goiy
        
        Args:
            score: Điểm của học sinh
            score_type: "chuan" hoặc "san"
            year: Năm học
        
        Returns:
            Dict chứa:
            - items: List ngành phù hợp
            - message: Thông báo
        """
        client = await self._get_client()
        
        payload = {
            "score": score,
            "score_type": score_type,
            "year": year,
        }
        
        logger.info(f"Suggesting majors for score: {score}")
        
        try:
            response = await client.post("/goiy", json=payload)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Suggested {len(data.get('items', []))} majors")
            
            return data
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error when suggesting majors: {str(e)}")
            return {"items": [], "message": "Có lỗi khi gợi ý ngành"}
    
    async def get_scholarships(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lấy thông tin học bổng.
        
        Endpoint: GET /hocbong
        
        Args:
            query: Từ khóa tìm kiếm (optional)
        
        Returns:
            List học bổng
        """
        client = await self._get_client()
        
        params = {}
        if query:
            params["q"] = query
        
        logger.info(f"Fetching scholarships with query: {query}")
        
        try:
            response = await client.get("/hocbong", params=params)
            response.raise_for_status()
            
            data = response.json()
            items = data.get("items", [])
            logger.info(f"Fetched {len(items)} scholarships")
            
            return items
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error when fetching scholarships: {str(e)}")
            return []


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

# Tạo một instance dùng chung cho toàn app
backend_client = BackendClient()

# Cleanup khi app shutdown
# Reflex sẽ tự động gọi close() nếu cần

