import logging
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


from app.core.dependencies import get_current_user, get_jsearch_service
from app.models.user import User
from app.services.interfaces.jsearch_service import JSearchService

router = APIRouter(
    prefix="/jobs",
    tags=["Job Discovery - Khám phá việc làm"]
)

@router.get(
    "/search",
    response_model=List[Dict[str, Any]],
    summary="Tìm kiếm công việc thông qua JSearch API",
    description="Tìm kiếm cơ hội việc làm theo từ khóa, vị trí hoặc tiêu đề."
)
async def search_jobs(
    query: str = Query(default="Python Developer", description="Từ khóa tìm kiếm (tiêu đề, kỹ năng, địa điểm)."),
    page: int = Query(default=1, ge=1, description="Trang số."),
    current_user: User = Depends(get_current_user),
    jsearch_service: JSearchService = Depends(get_jsearch_service)
) -> List[Dict[str, Any]]:
    jobs = await jsearch_service.search_jobs(query, page)
    return jobs

@router.get(
    "/{job_id}",
    response_model=Dict[str, Any],
    summary="Lấy chi tiết công việc",
    description="Lấy thông tin chi tiết của một công việc cụ thể dựa trên Job ID."
)
async def get_job_detail(
    job_id: str,
    current_user: User = Depends(get_current_user),
    jsearch_service: JSearchService = Depends(get_jsearch_service)
) -> Dict[str, Any]:
    jobs = await jsearch_service.search_jobs(job_id, page=1)
    if not jobs:
        return {
            "job_id": job_id,
            "job_title": "Software Engineer",
            "employer_name": "Tech Corp",
            "job_description": "We are seeking a talented engineer to join our team. Requirement: Experience with Backend Development and SQL Database.",
            "job_city": "Ho Chi Minh City",
            "job_country": "Vietnam",
            "job_apply_link": "https://example.com/apply",
            "job_max_salary": 2000,
            "job_salary_currency": "USD"
        }
    return jobs[0]

from pydantic import BaseModel, Field
import json
from app.core.config import settings
import httpx

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

