"""Backend API Client - Gọi các API endpoints của FastAPI backend."""

import logging
import os
from typing import Dict, Any, Optional, List

import httpx

logger = logging.getLogger(__name__)

# Đọc backend URL từ environment variable (cho Docker) hoặc dùng localhost (cho dev)
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
TIMEOUT = 30.0
DEFAULT_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


class BackendClient:
    """Client để tương tác với FastAPI backend."""

    def __init__(self, base_url: str = BACKEND_URL, timeout: float = TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client: Optional[httpx.AsyncClient] = None
        logger.info(f"Backend client initialized: {self.base_url}")

    async def _get_client(self) -> httpx.AsyncClient:
        if self.client is None:
            self.client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout, headers=DEFAULT_HEADERS)
        return self.client

    async def close(self):
        if self.client is not None:
            await self.client.aclose()
            self.client = None

    async def send_message(self, message: str, session_id: str = "default", use_context: bool = True) -> Dict[str, Any]:
        """Gửi tin nhắn tới backend."""
        client = await self._get_client()
        try:
            logger.info(f"Sending message to: {self.base_url}/chat/advanced")
            response = await client.post("/chat/advanced", json={"message": message, "session_id": session_id,
                                                                 "use_context": use_context})
            response.raise_for_status()
            logger.info(f"Response status: {response.status_code}")
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error when calling {self.base_url}: {str(e)}")
            raise

    async def reset_context(self, session_id: str = "default") -> Dict[str, Any]:
        """Reset context hội thoại."""
        client = await self._get_client()
        try:
            response = await client.post("/chat/context", json={"action": "reset", "session_id": session_id})
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error: {str(e)}")
            raise

    async def get_majors(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lấy danh sách ngành học."""
        client = await self._get_client()
        try:
            params = {"q": query} if query else {}
            response = await client.get("/nganh", params=params)
            response.raise_for_status()
            return response.json().get("items", [])
        except httpx.HTTPError:
            return []

    async def suggest_majors(self, score: float, score_type: str = "chuan", year: str = "2025") -> Dict[str, Any]:
        """Gợi ý ngành theo điểm số."""
        client = await self._get_client()
        try:
            response = await client.post("/goiy", json={"score": score, "score_type": score_type, "year": year})
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            return {"items": [], "message": "Có lỗi khi gợi ý ngành"}

    async def get_scholarships(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lấy thông tin học bổng."""
        client = await self._get_client()
        try:
            params = {"q": query} if query else {}
            response = await client.get("/hocbong", params=params)
            response.raise_for_status()
            return response.json().get("items", [])
        except httpx.HTTPError:
            return []


# Global backend client instance - khởi tạo lazy
_backend_client_instance: Optional[BackendClient] = None


def get_backend_client() -> BackendClient:
    """Get or create backend client instance."""
    global _backend_client_instance
    if _backend_client_instance is None:
        # Đọc BACKEND_URL mỗi lần để đảm bảo lấy đúng giá trị
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        logger.info(f"Initializing backend client with URL: {backend_url}")
        _backend_client_instance = BackendClient(base_url=backend_url)
    return _backend_client_instance


# Backward compatibility
backend_client = get_backend_client()
