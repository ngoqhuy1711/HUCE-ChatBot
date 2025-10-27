"""
Models - Pydantic models cho request/response validation

Tất cả API endpoints sử dụng các models này để:
1. Validate input từ client
2. Chuẩn hóa output về client
3. Tự động generate OpenAPI schema
"""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator


# ==============================================================================
# REQUEST MODELS - Định nghĩa cấu trúc request
# ==============================================================================


class ChatRequest(BaseModel):
    """Request cho endpoint /chat - Phân tích NLP đơn giản"""

    message: str = Field(..., min_length=1, description="Câu hỏi từ người dùng")

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate message không được rỗng sau khi strip"""
        if not v.strip():
            raise ValueError("Câu hỏi không được để trống")
        return v.strip()


class AdvancedChatRequest(BaseModel):
    """Request cho endpoint /chat/advanced - Chat đầy đủ với context"""

    message: str = Field(..., min_length=1, description="Câu hỏi từ người dùng")
    session_id: Optional[str] = Field(
        default="default", description="ID phiên hội thoại"
    )
    use_context: Optional[bool] = Field(
        default=True, description="Có sử dụng context không"
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Câu hỏi không được để trống")
        return v.strip()


class ContextRequest(BaseModel):
    """Request cho endpoint /chat/context - Quản lý context"""

    action: str = Field(..., description="Hành động: get, set, reset")
    session_id: Optional[str] = Field(default="default", description="ID phiên")
    context: Optional[Dict[str, Any]] = Field(
        default=None, description="Context mới (chỉ dùng khi action=set)"
    )

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        from constants import Validation

        if v not in Validation.VALID_ACTIONS:
            raise ValueError(
                f"Action không hợp lệ. Chỉ chấp nhận: {', '.join(Validation.VALID_ACTIONS)}"
            )
        return v


class SuggestMajorsRequest(BaseModel):
    """Request cho endpoint /goiy - Gợi ý ngành theo điểm"""

    score: float = Field(..., ge=0, le=30, description="Điểm số của học sinh")
    score_type: Optional[str] = Field(
        default="chuan", description="Loại điểm: 'chuan' hoặc 'san'"
    )
    year: Optional[str] = Field(default="2025", description="Năm học")

    @field_validator("score_type")
    @classmethod
    def validate_score_type(cls, v: str) -> str:
        from constants import Validation

        if v not in Validation.VALID_SCORE_TYPES:
            raise ValueError(
                f"Loại điểm không hợp lệ. Chỉ chấp nhận: {', '.join(Validation.VALID_SCORE_TYPES)}"
            )
        return v


# ==============================================================================
# RESPONSE MODELS - Định nghĩa cấu trúc response chuẩn
# ==============================================================================


class BaseResponse(BaseModel):
    """Base response model - Tất cả responses đều extend từ đây"""

    success: bool = Field(default=True, description="Trạng thái thành công")
    message: Optional[str] = Field(
        default=None, description="Thông điệp cho người dùng"
    )


class ErrorResponse(BaseResponse):
    """Response khi có lỗi"""

    success: bool = Field(default=False)
    error_code: Optional[str] = Field(default=None, description="Mã lỗi")
    error_detail: Optional[str] = Field(default=None, description="Chi tiết lỗi")


class DataResponse(BaseResponse):
    """Response chứa dữ liệu"""

    data: List[Dict[str, Any]] = Field(
        default_factory=list, description="Dữ liệu trả về"
    )
    count: int = Field(default=0, description="Số lượng kết quả")

    def __init__(self, **data):
        super().__init__(**data)
        if "count" not in data and "data" in data:
            self.count = len(data["data"])


class NLPAnalysisResponse(BaseResponse):
    """Response cho phân tích NLP"""

    intent: str = Field(..., description="Intent được nhận diện")
    confidence: float = Field(..., ge=0, le=1, description="Độ tin cậy")
    entities: List[Dict[str, Any]] = Field(
        default_factory=list, description="Entities trích xuất"
    )


class ChatResponse(BaseResponse):
    """Response cho chat đầy đủ"""

    analysis: Dict[str, Any] = Field(..., description="Kết quả phân tích NLP")
    response: Dict[str, Any] = Field(..., description="Response dữ liệu")
    context: Optional[Dict[str, Any]] = Field(
        default=None, description="Context sau khi xử lý"
    )


class ContextResponse(BaseResponse):
    """Response cho context management"""

    context: Dict[str, Any] = Field(
        default_factory=dict, description="Context hiện tại"
    )


# ==============================================================================
# UTILITY FUNCTIONS - Hàm tiện ích tạo response
# ==============================================================================


def create_success_response(
    data: Optional[List[Dict[str, Any]]] = None, message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Tạo response thành công chuẩn

    Args:
        data: Dữ liệu trả về (optional)
        message: Thông điệp (optional)

    Returns:
        Dict response chuẩn
    """
    if data is not None:
        return DataResponse(
            success=True, message=message, data=data, count=len(data)
        ).model_dump()
    else:
        return BaseResponse(success=True, message=message).model_dump()


def create_error_response(
    message: str, error_code: Optional[str] = None, error_detail: Optional[str] = None
) -> Dict[str, Any]:
    """
    Tạo response lỗi chuẩn

    Args:
        message: Thông điệp lỗi
        error_code: Mã lỗi (optional)
        error_detail: Chi tiết lỗi (optional)

    Returns:
        Dict response lỗi
    """
    return ErrorResponse(
        success=False, message=message, error_code=error_code, error_detail=error_detail
    ).model_dump()


def create_nlp_response(
    intent: str,
    confidence: float,
    entities: List[Dict[str, Any]],
    message: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Tạo response cho NLP analysis

    Args:
        intent: Intent được nhận diện
        confidence: Độ tin cậy
        entities: Danh sách entities
        message: Thông điệp (optional)

    Returns:
        Dict response NLP
    """
    return NLPAnalysisResponse(
        success=True,
        message=message,
        intent=intent,
        confidence=confidence,
        entities=entities,
    ).model_dump()
