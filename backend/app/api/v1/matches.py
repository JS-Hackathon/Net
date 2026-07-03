from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_matching_service
from app.models.user import User
from app.schemas.job_match import (
    MatchScoreResponse, MatchScoreData,
    MatchDetailResponse, MatchDetailData,
    MatchListResponse, MatchListData,
    BatchMatchRequest, BatchMatchResponse, BatchMatchData,
    MatchFeedbackRequest, SimpleMessageResponse, SimpleMessageData,
)
from app.services.interfaces.matching_service import IMatchingService

router = APIRouter(
    tags=["AI Matching - So khớp việc làm bằng AI"]
)


@router.post(
    "/jobs/{job_id}/match",
    response_model=MatchScoreResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tính điểm tương thích với một việc làm",
    description="So khớp hồ sơ ứng viên với một tin tuyển dụng bằng AI, trả về điểm tổng hợp và các điểm thành phần."
)
async def calculate_match(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: IMatchingService = Depends(get_matching_service),
) -> MatchScoreResponse:
    result = await service.calculate_match(user_id=current_user.id, job_id=uuid.UUID(job_id))
    await db.commit()
    return MatchScoreResponse(success=True, data=MatchScoreData(**result))


@router.post(
    "/jobs/batch-match",
    response_model=BatchMatchResponse,
    summary="So khớp nhiều việc làm cùng lúc",
    description="Tính match cho tối đa 50 việc làm đồng thời (giới hạn concurrency để tránh timeout)."
)
async def batch_match(
    payload: BatchMatchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: IMatchingService = Depends(get_matching_service),
) -> BatchMatchResponse:
    result = await service.batch_match(user_id=current_user.id, job_ids=payload.job_ids)
    await db.commit()
    return BatchMatchResponse(success=True, data=BatchMatchData(**result))


@router.get(
    "/matches",
    response_model=MatchListResponse,
    summary="Danh sách kết quả so khớp",
    description="Lấy danh sách các match đã tính, có lọc theo điểm tối thiểu và sắp xếp."
)
async def list_matches(
    min_score: float | None = Query(default=None, ge=0, le=100),
    sort: str = Query(default="score", pattern="^(score|date)$"),
    order: str = Query(default="desc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    service: IMatchingService = Depends(get_matching_service),
) -> MatchListResponse:
    result = await service.get_user_matches(
        user_id=current_user.id,
        min_score=min_score,
        sort=sort,
        order=order,
        page=page,
        per_page=per_page,
    )
    return MatchListResponse(success=True, data=MatchListData(**result))


@router.get(
    "/matches/{match_id}",
    response_model=MatchDetailResponse,
    summary="Chi tiết kết quả so khớp",
    description="Xem phân tích chi tiết một match: điểm thành phần, kỹ năng khớp/thiếu, gợi ý cải thiện."
)
async def get_match_detail(
    match_id: str,
    current_user: User = Depends(get_current_user),
    service: IMatchingService = Depends(get_matching_service),
) -> MatchDetailResponse:
    result = await service.get_match_detail(user_id=current_user.id, match_id=uuid.UUID(match_id))
    return MatchDetailResponse(success=True, data=MatchDetailData(**result))


@router.post(
    "/matches/{match_id}/feedback",
    response_model=SimpleMessageResponse,
    summary="Gửi phản hồi chất lượng so khớp",
    description="Người dùng gửi phản hồi (đã ứng tuyển, được phỏng vấn, đánh giá sao,...) để cải thiện thuật toán."
)
async def submit_feedback(
    match_id: str,
    payload: MatchFeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: IMatchingService = Depends(get_matching_service),
) -> SimpleMessageResponse:
    await service.submit_feedback(
        user_id=current_user.id,
        match_id=uuid.UUID(match_id),
        feedback_type=payload.feedback_type,
        user_rating=payload.user_rating,
        feedback_notes=payload.feedback_notes,
    )
    await db.commit()
    return SimpleMessageResponse(success=True, data=SimpleMessageData(message="Đã ghi nhận phản hồi của bạn"))
