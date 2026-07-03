import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, List, Optional

class ParsingMetricResponseData(BaseModel):
    field_name: str = Field(..., description="Tên trường thông tin")
    confidence_score: float = Field(..., description="Điểm tin cậy (0-100)")
    extraction_method: str = Field(..., description="Phương pháp trích xuất")
    validation_status: str = Field(..., description="Trạng thái xác thực")

    model_config = ConfigDict(from_attributes=True)

class ResumeAnalysisResponseData(BaseModel):
    id: uuid.UUID = Field(..., description="ID phân tích")
    resume_id: uuid.UUID = Field(..., description="ID CV được phân tích")
    status: str = Field(..., description="Trạng thái phân tích (pending, processing, completed, failed, reviewing)")
    confidence_score: Optional[float] = Field(default=None, description="Điểm tin cậy tổng quan (0-100)")
    parsed_data: Optional[Dict[str, Any]] = Field(default=None, description="Dữ liệu đã phân tích thành cấu trúc")
    error_message: Optional[str] = Field(default=None, description="Thông điệp lỗi nếu thất bại")
    parsing_duration: Optional[int] = Field(default=None, description="Thời gian phân tích (ms)")
    created_at: datetime = Field(..., description="Thời gian tạo")
    completed_at: Optional[datetime] = Field(default=None, description="Thời gian hoàn thành")

    model_config = ConfigDict(from_attributes=True)

class ResumeAnalysisResponse(BaseModel):
    success: bool = Field(default=True)
    data: ResumeAnalysisResponseData

class ParsingStatusResponseData(BaseModel):
    status: str = Field(..., description="Trạng thái hiện tại")
    progress_percentage: int = Field(..., description="Phần trăm tiến trình (0-100)")
    estimated_completion: Optional[datetime] = Field(default=None, description="Thời gian dự kiến hoàn thành")
    current_step: Optional[str] = Field(default=None, description="Bước hiện tại đang xử lý")

class ParsingStatusResponse(BaseModel):
    success: bool = Field(default=True)
    data: ParsingStatusResponseData

class AnalysisReviewRequest(BaseModel):
    corrections: Dict[str, Any] = Field(..., description="Các thông tin chỉnh sửa (dạng key: value)")
    approved: bool = Field(default=True, description="Đánh dấu đã phê duyệt dữ liệu")
