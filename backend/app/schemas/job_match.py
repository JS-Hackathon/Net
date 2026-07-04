import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any


# --- Auto Match (one-shot: suitable companies + interview scenario) ---

class AutoMatchCompany(BaseModel):
    job_id: str
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    match_score: float = 0.0
    reason: Optional[str] = None
    skills_required: List[str] = Field(default_factory=list)


class InterviewQuestion(BaseModel):
    category: Optional[str] = None
    question: Optional[str] = None
    assesses: Optional[str] = None
    answer_tip: Optional[str] = None


class InterviewScenario(BaseModel):
    opening: Optional[str] = None
    focus_skills: List[str] = Field(default_factory=list)
    gaps_to_prepare: List[str] = Field(default_factory=list)
    questions: List[InterviewQuestion] = Field(default_factory=list)
    preparation_tips: List[str] = Field(default_factory=list)
    closing: Optional[str] = None


class AutoMatchTarget(BaseModel):
    job_id: str
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None


class AutoMatchData(BaseModel):
    companies: List[AutoMatchCompany] = Field(default_factory=list)
    target: AutoMatchTarget
    interview_scenario: InterviewScenario


class AutoMatchResponse(BaseModel):
    success: bool = True
    data: AutoMatchData


class MatchScoreData(BaseModel):
    match_id: str
    overall_score: float
    skills_score: Optional[float] = None
    experience_score: Optional[float] = None
    education_score: Optional[float] = None
    location_score: Optional[float] = None
    confidence_score: Optional[float] = None
    needs_review: bool = False
    processing_time: Optional[int] = None
    created_at: Optional[datetime] = None


class MatchScoreResponse(BaseModel):
    success: bool = Field(default=True)
    data: MatchScoreData


class JobBrief(BaseModel):
    id: str
    title: str
    company: str
    location: Optional[str] = None
    employment_type: Optional[str] = None


class SkillMatchData(BaseModel):
    skill_name: str
    skill_category: Optional[str] = None
    required_proficiency: Optional[str] = None
    candidate_proficiency: Optional[str] = None
    match_type: Optional[str] = None
    match_score: Optional[float] = None


class MatchAnalysis(BaseModel):
    summary: Optional[str] = None
    strengths: List[Any] = Field(default_factory=list)
    weaknesses: List[Any] = Field(default_factory=list)
    missing_skills: List[Any] = Field(default_factory=list)
    areas_for_improvement: List[Any] = Field(default_factory=list)
    recommendation: Dict[str, Any] = Field(default_factory=dict)
    skills_matches: List[SkillMatchData] = Field(default_factory=list)


class MatchDetailData(BaseModel):
    id: str
    job: Optional[JobBrief] = None
    overall_score: float
    skills_score: Optional[float] = None
    experience_score: Optional[float] = None
    education_score: Optional[float] = None
    location_score: Optional[float] = None
    confidence_score: Optional[float] = None
    needs_review: bool = False
    analysis: MatchAnalysis
    processing_time: Optional[int] = None
    created_at: Optional[datetime] = None


class MatchDetailResponse(BaseModel):
    success: bool = Field(default=True)
    data: MatchDetailData


class MatchListItem(BaseModel):
    match_id: str
    job: JobBrief
    overall_score: float
    match_summary: Optional[str] = None
    needs_review: bool = False
    created_at: Optional[datetime] = None


class Pagination(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int


class MatchListData(BaseModel):
    matches: List[MatchListItem]
    pagination: Pagination


class MatchListResponse(BaseModel):
    success: bool = Field(default=True)
    data: MatchListData


class BatchMatchRequest(BaseModel):
    job_ids: List[uuid.UUID] = Field(..., min_length=1, description="Danh sách ID job cần so khớp")


class BatchMatchItem(BaseModel):
    job_id: str
    match_id: Optional[str] = None
    overall_score: Optional[float] = None
    status: str


class BatchProcessingSummary(BaseModel):
    total_jobs: int
    successful: int
    failed: int
    average_processing_time: int


class BatchMatchData(BaseModel):
    matches: List[BatchMatchItem]
    processing_summary: BatchProcessingSummary


class BatchMatchResponse(BaseModel):
    success: bool = Field(default=True)
    data: BatchMatchData


class MatchFeedbackRequest(BaseModel):
    feedback_type: Optional[str] = Field(default=None, description="applied, interviewed, hired, rejected")
    user_rating: Optional[int] = Field(default=None, ge=1, le=5)
    feedback_notes: Optional[str] = Field(default=None)


class SimpleMessageData(BaseModel):
    message: str


class SimpleMessageResponse(BaseModel):
    success: bool = Field(default=True)
    data: SimpleMessageData
