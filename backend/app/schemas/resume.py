import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import List

class ResumeResponseData(BaseModel):
    id: uuid.UUID = Field(..., description="ID của resume")
    filename: str = Field(..., description="Tên file lưu trữ hệ thống")
    original_filename: str = Field(..., description="Tên file gốc người dùng tải lên")
    file_size: int = Field(..., description="Kích thước file (bytes)")
    file_type: str = Field(..., description="Loại file (pdf, docx)")
    upload_status: str = Field(..., description="Trạng thái tải lên (uploading, completed, failed, processing)")
    is_primary: bool = Field(..., description="Đặt làm CV chính")
    text_extraction_status: str | None = Field(default=None, description="Trạng thái trích xuất văn bản")
    created_at: datetime = Field(..., description="Thời gian tải lên")
    updated_at: datetime = Field(..., description="Thời gian cập nhật")

    model_config = ConfigDict(from_attributes=True)

class ResumeResponse(BaseModel):
    success: bool = Field(default=True)
    data: ResumeResponseData

class ResumeListResponseData(BaseModel):
    resumes: List[ResumeResponseData] = Field(..., description="Danh sách CV")
    total: int = Field(..., description="Tổng số lượng CV")

class ResumeListResponse(BaseModel):
    success: bool = Field(default=True)
    data: ResumeListResponseData

class ResumeDownloadResponseData(BaseModel):
    download_url: str = Field(..., description="Đường dẫn tải CV xuống")
    expires_at: datetime | None = Field(default=None, description="Thời gian hết hạn của liên kết tải xuống")

class ResumeDownloadResponse(BaseModel):
    success: bool = Field(default=True)
    data: ResumeDownloadResponseData
