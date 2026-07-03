import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional

# --- Nested Profile Structures ---

class WorkExperienceSchema(BaseModel):
    title: str = Field(..., description="Chức danh công việc")
    company: str = Field(..., description="Tên công ty")
    location: Optional[str] = Field(default=None, description="Địa điểm công ty")
    start_date: str = Field(..., description="Ngày bắt đầu (YYYY-MM-DD hoặc YYYY)")
    end_date: Optional[str] = Field(default=None, description="Ngày kết thúc (NULL nếu đang làm)")
    is_current: bool = Field(default=False, description="Công việc hiện tại")
    description: str = Field(..., description="Mô tả chi tiết công việc")
    key_achievements: List[str] = Field(default_factory=list, description="Thành tựu chính đạt được")
    technologies_used: List[str] = Field(default_factory=list, description="Công nghệ sử dụng")

class EducationSchema(BaseModel):
    degree: str = Field(..., description="Bằng cấp")
    field_of_study: Optional[str] = Field(default=None, description="Ngành học")
    institution: str = Field(..., description="Trường đào tạo")
    location: Optional[str] = Field(default=None, description="Địa điểm")
    graduation_date: Optional[str] = Field(default=None, description="Ngày tốt nghiệp (YYYY-MM-DD hoặc YYYY)")
    gpa: Optional[str] = Field(default=None, description="Điểm trung bình học tập GPA")
    honors: List[str] = Field(default_factory=list, description="Giải thưởng/Danh hiệu")

class TechnicalSkillSchema(BaseModel):
    name: str = Field(..., description="Tên kỹ năng")
    category: str = Field(..., description="Danh mục kỹ năng (Programming, Framework, Tool,...)")
    proficiency: str = Field(..., description="Mức độ thành thạo (Beginner, Intermediate, Advanced, Expert)")
    years_experience: Optional[float] = Field(default=None, description="Số năm kinh nghiệm")

class SoftSkillSchema(BaseModel):
    name: str = Field(..., description="Tên kỹ năng mềm")
    description: Optional[str] = Field(default=None, description="Mô tả kỹ năng mềm")

class CertificationSchema(BaseModel):
    name: str = Field(..., description="Tên chứng chỉ")
    issuer: str = Field(..., description="Nơi cấp")
    issue_date: Optional[str] = Field(default=None, description="Ngày cấp")
    expiry_date: Optional[str] = Field(default=None, description="Ngày hết hạn")
    credential_id: Optional[str] = Field(default=None, description="Mã chứng chỉ")
    verification_url: Optional[str] = Field(default=None, description="Liên kết xác minh")

class LanguageSchema(BaseModel):
    language: str = Field(..., description="Ngôn ngữ")
    proficiency: str = Field(..., description="Mức độ thông thạo (Basic, Conversational, Fluent, Native)")

class ProjectSchema(BaseModel):
    name: str = Field(..., description="Tên dự án")
    description: str = Field(..., description="Mô tả chi tiết dự án")
    technologies: List[str] = Field(default_factory=list, description="Công nghệ sử dụng trong dự án")
    url: Optional[str] = Field(default=None, description="Đường dẫn dự án")
    start_date: Optional[str] = Field(default=None, description="Ngày bắt đầu")
    end_date: Optional[str] = Field(default=None, description="Ngày kết thúc")

class AchievementSchema(BaseModel):
    title: str = Field(..., description="Tiêu đề giải thưởng/thành tựu")
    description: Optional[str] = Field(default=None, description="Mô tả chi tiết")
    date: Optional[str] = Field(default=None, description="Ngày đạt được")
    issuer: Optional[str] = Field(default=None, description="Nơi cấp/tổ chức khen thưởng")


# --- Main Profile Schemas ---

class CandidateProfileResponseData(BaseModel):
    id: uuid.UUID = Field(..., description="ID hồ sơ")
    user_id: uuid.UUID = Field(..., description="ID người dùng")
    source_analysis_id: Optional[uuid.UUID] = Field(default=None, description="ID phân tích nguồn gốc")

    # Personal Info
    full_name: Optional[str] = Field(default=None, description="Họ và tên")
    email: Optional[str] = Field(default=None, description="Email liên hệ")
    phone: Optional[str] = Field(default=None, description="Số điện thoại")
    location: Optional[str] = Field(default=None, description="Địa chỉ nơi ở")
    linkedin_url: Optional[str] = Field(default=None, description="Đường dẫn LinkedIn")
    portfolio_url: Optional[str] = Field(default=None, description="Đường dẫn Portfolio")
    github_url: Optional[str] = Field(default=None, description="Đường dẫn Github")
    website_url: Optional[str] = Field(default=None, description="Đường dẫn trang cá nhân khác")

    # Professional Summary
    professional_summary: Optional[str] = Field(default=None, description="Tóm tắt chuyên môn")
    career_objective: Optional[str] = Field(default=None, description="Mục tiêu nghề nghiệp")
    years_of_experience: Optional[int] = Field(default=None, description="Số năm kinh nghiệm thực tế")
    current_role: Optional[str] = Field(default=None, description="Công việc hiện tại")
    current_company: Optional[str] = Field(default=None, description="Công ty hiện tại")
    salary_expectation_min: Optional[int] = Field(default=None, description="Kỳ vọng lương tối thiểu (VND/USD)")
    salary_expectation_max: Optional[int] = Field(default=None, description="Kỳ vọng lương tối đa (VND/USD)")
    availability: Optional[str] = Field(default=None, description="Thời gian sẵn sàng làm việc")

    # Structured Collections
    work_experience: List[WorkExperienceSchema] = Field(default_factory=list, description="Kinh nghiệm làm việc")
    education: List[EducationSchema] = Field(default_factory=list, description="Học vấn")
    technical_skills: List[TechnicalSkillSchema] = Field(default_factory=list, description="Kỹ năng chuyên môn")
    soft_skills: List[SoftSkillSchema] = Field(default_factory=list, description="Kỹ năng mềm")
    certifications: List[CertificationSchema] = Field(default_factory=list, description="Chứng chỉ")
    languages: List[LanguageSchema] = Field(default_factory=list, description="Ngoại ngữ")
    projects: List[ProjectSchema] = Field(default_factory=list, description="Dự án thực tế")
    achievements: List[AchievementSchema] = Field(default_factory=list, description="Giải thưởng & Thành tựu")

    # Metadata
    completeness_score: float = Field(..., description="Điểm hoàn thiện hồ sơ")
    profile_strength: str = Field(..., description="Đánh giá sức mạnh hồ sơ (basic, good, strong, excellent)")
    is_public: bool = Field(..., description="Hồ sơ công khai")
    is_searchable: bool = Field(..., description="Có thể tìm kiếm hồ sơ")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CandidateProfileResponse(BaseModel):
    success: bool = Field(default=True)
    data: CandidateProfileResponseData

class ProfileSectionUpdateRequest(BaseModel):
    section: str = Field(..., description="Tên phân đoạn cần cập nhật (e.g. work_experience, education, personal_info, summary)")
    data: Dict[str, Any] = Field(..., description="Dữ liệu dạng JSON chứa thông tin cập nhật cho phân đoạn đó")

class CompletenessSuggestion(BaseModel):
    section: str = Field(..., description="Tên phần hồ sơ")
    message: str = Field(..., description="Lời gợi ý bổ sung")
    priority: str = Field(..., description="Độ ưu tiên gợi ý (high, medium, low)")

class ProfileCompletenessResponseData(BaseModel):
    overall_score: float = Field(..., description="Điểm hoàn thiện tổng quan (0-100)")
    section_scores: Dict[str, float] = Field(..., description="Điểm hoàn thiện theo từng phần")
    suggestions: List[CompletenessSuggestion] = Field(..., description="Danh sách các gợi ý cải thiện")
    missing_fields: Dict[str, List[str]] = Field(..., description="Các trường còn thiếu theo từng phần")

class ProfileCompletenessResponse(BaseModel):
    success: bool = Field(default=True)
    data: ProfileCompletenessResponseData

class ProfileExportRequest(BaseModel):
    format: str = Field(..., description="Định dạng xuất file (pdf hoặc json)")
    sections: Optional[List[str]] = Field(default=None, description="Danh sách các phân đoạn xuất (mặc định xuất hết)")

class ProfileExportResponseData(BaseModel):
    download_url: str = Field(..., description="Đường dẫn tải file xuất")
    expires_at: datetime = Field(..., description="Thời gian hết hạn liên kết")
    file_name: str = Field(..., description="Tên file")

class ProfileExportResponse(BaseModel):
    success: bool = Field(default=True)
    data: ProfileExportResponseData
