import uuid
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_job_matching_service
from app.models.user import User
from app.models.candidate_profile import CandidateProfile
from app.models.job_match import JobMatch
from app.schemas.job_matching import (
    CompareRequest,
    CompareResponse,
    CandidateProfileInput,
    ProfileSkill,
    ProfileExperience,
    ProfileProject,
    RequirementMatchResult
)
from app.services.interfaces.job_matching_service import IJobMatchingService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/matching",
    tags=["AI Job Matching - So khớp cơ hội nghề nghiệp"]
)

@router.post(
    "/compare",
    response_model=CompareResponse,
    summary="So khớp hồ sơ ứng viên với yêu cầu công việc",
    description="Tính toán mức độ phù hợp (Match Score) giữa CV ứng viên và JD tuyển dụng."
)
async def compare_jd_cv(
    payload: CompareRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    matching_service: IJobMatchingService = Depends(get_job_matching_service)
) -> CompareResponse:
    # 1. Fetch Candidate Profile
    try:
        profile_uuid = uuid.UUID(payload.candidate_profile_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã định danh hồ sơ ứng viên không hợp lệ."
        )

    stmt = select(CandidateProfile).where(CandidateProfile.id == profile_uuid)
    profile = (await db.execute(stmt)).scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hồ sơ ứng viên không tồn tại."
        )

    if profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập hồ sơ này."
        )

    # 2. Map CandidateProfile to CandidateProfileInput schema
    # Map skills
    skills_input = []
    if profile.technical_skills:
        # technical_skills in DB is JSON: list of dict or dict
        # Typically looks like: [{"name": "fastapi", "category": "Backend"}, ...]
        raw_skills = profile.technical_skills
        if isinstance(raw_skills, list):
            for sk in raw_skills:
                skills_input.append(ProfileSkill(
                    canonical=sk.get("name", sk.get("canonical", "Unknown")),
                    category=sk.get("category", "General"),
                    confidence=float(sk.get("confidence", 1.0)),
                    mapping_method=sk.get("mapping_method", "dictionary")
                ))
        elif isinstance(raw_skills, dict):
            for cat, items in raw_skills.items():
                if isinstance(items, list):
                    for item in items:
                        skills_input.append(ProfileSkill(
                            canonical=item if isinstance(item, str) else item.get("name", "Unknown"),
                            category=cat,
                            confidence=1.0,
                            mapping_method="dictionary"
                        ))

    # Map experience
    exp_input = []
    if profile.work_experience:
        raw_exp = profile.work_experience
        if isinstance(raw_exp, list):
            for ex in raw_exp:
                exp_input.append(ProfileExperience(
                    title=ex.get("title", ex.get("role", "Unknown")),
                    company=ex.get("company", "Unknown"),
                    duration_months=int(ex.get("duration_months", 0)),
                    description=ex.get("description", ex.get("responsibilities", ""))
                ))

    # Map projects
    proj_input = []
    if profile.projects:
        raw_proj = profile.projects
        if isinstance(raw_proj, list):
            for pr in raw_proj:
                proj_input.append(ProfileProject(
                    name=pr.get("name", "Unknown"),
                    description=pr.get("description", ""),
                    technologies=pr.get("technologies", [])
                ))

    # Map certifications
    cert_input = []
    if profile.certifications:
        raw_cert = profile.certifications
        if isinstance(raw_cert, list):
            cert_input = [c if isinstance(c, str) else c.get("name", "Unknown") for c in raw_cert]

    profile_input = CandidateProfileInput(
        user_id=str(profile.user_id),
        skills=skills_input,
        experience=exp_input,
        projects=proj_input,
        certifications=cert_input,
        summary=profile.professional_summary or ""
    )

    # 3. Execute Matching
    match_matrix = await matching_service.evaluate_all(profile_input, payload.requirements)

    # 4. Compute Weighted Overall Match Score
    # overall_score = sum(confidence * priority_score) / sum(priority_score) * 100
    total_priority_weight = sum(res.priority.score for res in match_matrix)
    if total_priority_weight > 0:
        weighted_score = sum(res.confidence * res.priority.score for res in match_matrix) / total_priority_weight * 100
        overall_score = round(weighted_score, 2)
    else:
        overall_score = 0.0

    # 5. Save JobMatch to database
    job_match = JobMatch(
        user_id=current_user.id,
        job_id=payload.job_id,
        job_title=payload.job_title,
        company_name=payload.company_name,
        overall_score=overall_score,
        match_matrix=[res.model_dump() for res in match_matrix]
    )
    db.add(job_match)
    await db.commit()
    await db.refresh(job_match)

    return CompareResponse(
        match_id=str(job_match.id),
        overall_score=overall_score,
        match_matrix=match_matrix
    )

@router.get(
    "/history",
    response_model=List[dict],
    summary="Lấy lịch sử so khớp công việc của ứng viên",
    description="Trả về danh sách tóm tắt tất cả các lượt so khớp công việc trước đây."
)
async def get_match_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[dict]:
    stmt = select(JobMatch).where(JobMatch.user_id == current_user.id).order_by(JobMatch.created_at.desc())
    matches = (await db.execute(stmt)).scalars().all()
    
    return [
        {
            "match_id": str(m.id),
            "job_id": m.job_id,
            "job_title": m.job_title,
            "company_name": m.company_name,
            "overall_score": float(m.overall_score),
            "created_at": m.created_at.isoformat()
        }
        for m in matches
    ]

@router.get(
    "/history/{match_id}",
    response_model=CompareResponse,
    summary="Chi tiết lịch sử so khớp công việc",
    description="Truy xuất lại chi tiết bảng phân tích so khớp Requirement Matrix của một lượt so khớp cụ thể."
)
async def get_match_detail(
    match_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> CompareResponse:
    try:
        match_uuid = uuid.UUID(match_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã định danh lượt so khớp không hợp lệ."
        )

    stmt = select(JobMatch).where(JobMatch.id == match_uuid)
    job_match = (await db.execute(stmt)).scalar_one_or_none()

    if not job_match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lượt so khớp không tồn tại."
        )

    if job_match.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xem thông tin này."
        )

    # Convert match_matrix JSON back to Pydantic models
    matrix_list = []
    for item in job_match.match_matrix:
        matrix_list.append(RequirementMatchResult(**item))

    return CompareResponse(
        match_id=str(job_match.id),
        overall_score=float(job_match.overall_score),
        match_matrix=matrix_list
    )
