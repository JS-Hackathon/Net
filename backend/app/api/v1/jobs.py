from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import logging
from typing import List, Dict, Any
import json
from pydantic import BaseModel, Field
import httpx

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_job_discovery_service, get_ai_provider
from app.models.user import User
from app.schemas.job import (
    JobSearchResponse, JobSearchResponseData,
    JobDetailResponse, JobDetailData,
    BookmarkActionResponse, BookmarkActionData,
    BookmarkListResponse, BookmarkListData,
    SavedSearchRequest, SavedSearchResponse, SavedSearchData,
    SavedSearchListResponse, SavedSearchListData,
    RecommendationListResponse, RecommendationListData,
)
from app.services.interfaces.job_discovery_service import IJobDiscoveryService
from app.core.config import settings

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/jobs",
    tags=["Job Discovery - Khám phá việc làm"]
)

@router.get(
    "/search",
    response_model=JobSearchResponse,
    summary="Tìm kiếm việc làm",
    description="Tìm kiếm việc làm qua JSearch API (có cache 4 giờ), hỗ trợ lọc theo địa điểm, mức lương, hình thức làm việc và phân trang."
)
async def search_jobs(
    q: str = Query(..., description="Từ khóa tìm kiếm (chức danh, kỹ năng)"),
    location: str | None = Query(default=None),
    employment_type: str | None = Query(default=None, description="remote, hybrid, on-site"),
    experience_level: str | None = Query(default=None, description="entry, mid, senior"),
    salary_min: int | None = Query(default=None, ge=0),
    remote: bool = Query(default=False),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: IJobDiscoveryService = Depends(get_job_discovery_service),
) -> JobSearchResponse:
    result = await service.search_jobs(
        user_id=current_user.id,
        query=q,
        location=location,
        employment_type=employment_type,
        experience_level=experience_level,
        salary_min=salary_min,
        remote_only=remote,
        page=page,
        per_page=per_page,
    )
    await db.commit()
    return JobSearchResponse(success=True, data=JobSearchResponseData(**result))


@router.get(
    "/bookmarks",
    response_model=BookmarkListResponse,
    summary="Danh sách việc làm đã lưu",
    description="Lấy danh sách các tin tuyển dụng người dùng đã bookmark."
)
async def get_bookmarks(
    current_user: User = Depends(get_current_user),
    service: IJobDiscoveryService = Depends(get_job_discovery_service),
) -> BookmarkListResponse:
    bookmarks = await service.get_bookmarks(user_id=current_user.id)
    return BookmarkListResponse(
        success=True,
        data=BookmarkListData(bookmarks=bookmarks, total=len(bookmarks)),
    )


@router.get(
    "/recommendations",
    response_model=RecommendationListResponse,
    summary="Gợi ý việc làm theo hồ sơ",
    description="Gợi ý các việc làm phù hợp nhất dựa trên kỹ năng trong hồ sơ ứng viên."
)
async def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: IJobDiscoveryService = Depends(get_job_discovery_service),
) -> RecommendationListResponse:
    recs = await service.get_recommendations(user_id=current_user.id)
    await db.commit()
    return RecommendationListResponse(
        success=True,
        data=RecommendationListData(recommendations=recs, total=len(recs)),
    )


@router.get(
    "/saved-searches",
    response_model=SavedSearchListResponse,
    summary="Danh sách tìm kiếm đã lưu",
)
async def list_saved_searches(
    current_user: User = Depends(get_current_user),
    service: IJobDiscoveryService = Depends(get_job_discovery_service),
) -> SavedSearchListResponse:
    searches = await service.list_saved_searches(user_id=current_user.id)
    return SavedSearchListResponse(
        success=True,
        data=SavedSearchListData(saved_searches=searches, total=len(searches)),
    )


@router.post(
    "/saved-searches",
    response_model=SavedSearchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Lưu bộ tiêu chí tìm kiếm",
    description="Lưu lại tiêu chí tìm kiếm để nhận thông báo khi có việc làm mới phù hợp."
)
async def create_saved_search(
    payload: SavedSearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: IJobDiscoveryService = Depends(get_job_discovery_service),
) -> SavedSearchResponse:
    saved = await service.create_saved_search(
        user_id=current_user.id,
        name=payload.name,
        criteria=payload.search_criteria,
        alert_frequency=payload.alert_frequency,
    )
    await db.commit()
    return SavedSearchResponse(success=True, data=SavedSearchData(**saved))


@router.get(
    "/{job_id}",
    response_model=JobDetailResponse,
    summary="Chi tiết việc làm",
    description="Xem thông tin chi tiết một tin tuyển dụng và ghi nhận lượt xem."
)
async def get_job_details(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: IJobDiscoveryService = Depends(get_job_discovery_service),
) -> JobDetailResponse:
    job = await service.get_job_details(user_id=current_user.id, job_id=uuid.UUID(job_id))
    await db.commit()
    return JobDetailResponse(success=True, data=JobDetailData(**job))


@router.post(
    "/{job_id}/bookmark",
    response_model=BookmarkActionResponse,
    summary="Lưu việc làm",
)
async def bookmark_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: IJobDiscoveryService = Depends(get_job_discovery_service),
) -> BookmarkActionResponse:
    await service.bookmark_job(user_id=current_user.id, job_id=uuid.UUID(job_id))
    await db.commit()
    return BookmarkActionResponse(
        success=True,
        data=BookmarkActionData(message="Đã lưu việc làm", is_bookmarked=True),
    )


@router.delete(
    "/{job_id}/bookmark",
    response_model=BookmarkActionResponse,
    summary="Bỏ lưu việc làm",
)
async def unbookmark_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: IJobDiscoveryService = Depends(get_job_discovery_service),
) -> BookmarkActionResponse:
    await service.unbookmark_job(user_id=current_user.id, job_id=uuid.UUID(job_id))
    await db.commit()
    return BookmarkActionResponse(
        success=True,
        data=BookmarkActionData(message="Đã bỏ lưu việc làm", is_bookmarked=False),
    )


# --- Preserved: AI extract-requirements endpoint from feat-matching (kept) ---
class ExtractRequest(BaseModel):
    job_description: str = Field(..., description="Raw text of the job description.")

@router.post(
    "/extract-requirements",
    response_model=List[Dict[str, Any]],
    summary="Trích xuất yêu cầu công việc từ mô tả thô (JD)",
    description="Sử dụng AI để phân tích mô tả công việc thô và trích xuất danh sách các yêu cầu kỹ thuật có cấu trúc."
)
async def extract_requirements(
    payload: ExtractRequest,
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        # Fallback mocks
        return [
            {
                "id": "REQ1",
                "text": "Experience with Backend Development",
                "canonical": "Backend Development",
                "category": "Backend Development",
                "section": "must_have",
                "priority": "CRITICAL"
            },
            {
                "id": "REQ2",
                "text": "Knowledge of SQL Database",
                "canonical": "SQL Database",
                "category": "SQL Database",
                "section": "required",
                "priority": "HIGH"
            }
        ]

    prompt = (
        "You are an expert technical recruiter. Analyze the following job description text "
        "and extract a list of structured requirements. "
        "Return strictly a JSON array of objects. Do not include markdown formatting (like ```json) or any explanations.\n\n"
        "Each object in the array must strictly have these fields:\n"
        "- 'id': unique string identifier (e.g. 'REQ1', 'REQ2')\n"
        "- 'text': raw requirement sentence from JD\n"
        "- 'canonical': canonical technical concept (e.g. 'Backend Development', 'Containerization', 'SQL Database', 'Frontend Development')\n"
        "- 'category': high-level category\n"
        "- 'section': must be one of ['must_have', 'required', 'preferred', 'nice_to_have']\n"
        "- 'priority': must be one of ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']\n\n"
        f"Job Description:\n{payload.job_description}"
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=body, headers=headers, timeout=15.0)
            response.raise_for_status()
            res_data = response.json()
            content = res_data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(content)
        except Exception as e:
            logger.error(f"Failed to extract requirements via Gemini: {e}")
            # Fallback mocks on error
            return [
                {
                    "id": "REQ1",
                    "text": "Experience with software engineering principles",
                    "canonical": "Backend Development",
                    "category": "Software",
                    "section": "must_have",
                    "priority": "CRITICAL"
                }
            ]

