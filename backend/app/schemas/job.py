import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any


class JobSummary(BaseModel):
    id: str = Field(..., description="ID job trong hệ thống")
    external_id: str = Field(..., description="ID job từ JSearch")
    title: str = Field(..., description="Tiêu đề công việc")
    company: str = Field(..., description="Tên công ty")
    company_logo_url: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None)
    employment_type: Optional[str] = Field(default=None, description="remote, hybrid, on-site,...")
    experience_level: Optional[str] = Field(default=None, description="entry, mid, senior")
    salary_range: Optional[str] = Field(default=None, description="Khoảng lương đã định dạng")
    salary_min: Optional[int] = Field(default=None)
    salary_max: Optional[int] = Field(default=None)
    skills_required: List[Any] = Field(default_factory=list)
    posted_date: Optional[datetime] = Field(default=None)
    application_url: Optional[str] = Field(default=None)
    is_bookmarked: bool = Field(default=False)

    model_config = ConfigDict(from_attributes=True)


class JobDetailData(JobSummary):
    description: Optional[str] = Field(default=None)
    requirements: Optional[str] = Field(default=None)
    benefits: Optional[str] = Field(default=None)
    industry: Optional[str] = Field(default=None)
    source_platform: Optional[str] = Field(default=None)
    job_type: Optional[str] = Field(default=None)


class Pagination(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int


class JobSearchResponseData(BaseModel):
    jobs: List[JobSummary]
    pagination: Pagination


class JobSearchResponse(BaseModel):
    success: bool = Field(default=True)
    data: JobSearchResponseData


class JobDetailResponse(BaseModel):
    success: bool = Field(default=True)
    data: JobDetailData


class BookmarkActionData(BaseModel):
    message: str
    is_bookmarked: bool


class BookmarkActionResponse(BaseModel):
    success: bool = Field(default=True)
    data: BookmarkActionData


class BookmarkItem(BaseModel):
    job: JobSummary
    bookmarked_at: datetime


class BookmarkListData(BaseModel):
    bookmarks: List[BookmarkItem]
    total: int


class BookmarkListResponse(BaseModel):
    success: bool = Field(default=True)
    data: BookmarkListData


class SavedSearchRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    search_criteria: Dict[str, Any] = Field(..., description="Tiêu chí tìm kiếm đã lưu")
    alert_frequency: str = Field(default="daily", description="daily, weekly, immediate")


class SavedSearchData(BaseModel):
    id: str
    name: str
    search_criteria: Dict[str, Any]
    alert_frequency: str
    is_active: bool
    created_at: datetime


class SavedSearchResponse(BaseModel):
    success: bool = Field(default=True)
    data: SavedSearchData


class SavedSearchListData(BaseModel):
    saved_searches: List[SavedSearchData]
    total: int


class SavedSearchListResponse(BaseModel):
    success: bool = Field(default=True)
    data: SavedSearchListData


class RecommendationItem(BaseModel):
    job: JobSummary
    recommendation_score: float
    recommendation_reason: str


class RecommendationListData(BaseModel):
    recommendations: List[RecommendationItem]
    total: int


class RecommendationListResponse(BaseModel):
    success: bool = Field(default=True)
    data: RecommendationListData
