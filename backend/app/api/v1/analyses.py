from fastapi import APIRouter, Depends, Request, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_resume_analysis_service
from app.models.user import User
from app.schemas.resume_analysis import (
    ResumeAnalysisResponse,
    ResumeAnalysisResponseData,
    ParsingStatusResponse,
    ParsingStatusResponseData,
    AnalysisReviewRequest
)
from app.services.interfaces.resume_analysis_service import IResumeAnalysisService

router = APIRouter(
    tags=["Resume Analysis - Hệ thống phân tích CV"]
)

@router.post(
    "/resumes/{resume_id}/parse",
    response_model=ResumeAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Yêu cầu phân tích lại CV",
    description="Kích hoạt quá trình phân tích CV thủ công chạy ngầm."
)
async def parse_resume(
    resume_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    analysis_service: IResumeAnalysisService = Depends(get_resume_analysis_service)
) -> ResumeAnalysisResponse:
    analysis = await analysis_service.parse_resume_background(
        user_id=current_user.id,
        resume_id=uuid.UUID(resume_id)
    )
    
    background_tasks.add_task(
        analysis_service.run_extraction_and_parsing_sync,
        analysis_id=analysis.id
    )
    
    await db.commit()
    await db.refresh(analysis)
    
    return ResumeAnalysisResponse(
        success=True,
        data=ResumeAnalysisResponseData.model_validate(analysis)
    )

@router.get(
    "/analyses/{analysis_id}",
    response_model=ResumeAnalysisResponse,
    summary="Lấy kết quả phân tích CV",
    description="Lấy dữ liệu cấu trúc chi tiết đã phân tích được của một CV."
)
async def get_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    analysis_service: IResumeAnalysisService = Depends(get_resume_analysis_service)
) -> ResumeAnalysisResponse:
    analysis = await analysis_service.get_analysis(
        user_id=current_user.id,
        analysis_id=uuid.UUID(analysis_id)
    )
    return ResumeAnalysisResponse(
        success=True,
        data=ResumeAnalysisResponseData.model_validate(analysis)
    )

@router.get(
    "/analyses/{analysis_id}/status",
    response_model=ParsingStatusResponse,
    summary="Theo dõi tiến độ phân tích",
    description="Endpoint thăm dò tiến độ xử lý và trạng thái phân tích hiện tại để thực hiện cơ chế Polling."
)
async def get_parsing_status(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    analysis_service: IResumeAnalysisService = Depends(get_resume_analysis_service)
) -> ParsingStatusResponse:
    status_data = await analysis_service.get_parsing_status(
        user_id=current_user.id,
        analysis_id=uuid.UUID(analysis_id)
    )
    return ParsingStatusResponse(
        success=True,
        data=ParsingStatusResponseData(**status_data)
    )

@router.put(
    "/analyses/{analysis_id}/review",
    response_model=ResumeAnalysisResponse,
    summary="Phê duyệt kết quả phân tích",
    description="Người dùng gửi xác nhận dữ liệu đã chỉnh sửa để chính thức đồng bộ thông tin phân tích vào hồ sơ ứng viên."
)
async def review_analysis(
    analysis_id: str,
    payload: AnalysisReviewRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    analysis_service: IResumeAnalysisService = Depends(get_resume_analysis_service)
) -> ResumeAnalysisResponse:
    analysis = await analysis_service.submit_review(
        user_id=current_user.id,
        analysis_id=uuid.UUID(analysis_id),
        corrections=payload.corrections,
        approved=payload.approved
    )
    await db.commit()
    await db.refresh(analysis)
    return ResumeAnalysisResponse(
        success=True,
        data=ResumeAnalysisResponseData.model_validate(analysis)
    )

@router.post(
    "/analyses/{analysis_id}/retry",
    response_model=ResumeAnalysisResponse,
    summary="Thử lại phân tích thất bại",
    description="Thử lại quá trình phân tích CV bị lỗi do timeout hoặc lỗi hệ thống AI."
)
async def retry_parsing(
    analysis_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    analysis_service: IResumeAnalysisService = Depends(get_resume_analysis_service)
) -> ResumeAnalysisResponse:
    analysis = await analysis_service.retry_parsing(
        user_id=current_user.id,
        analysis_id=uuid.UUID(analysis_id)
    )
    
    background_tasks.add_task(
        analysis_service.run_extraction_and_parsing_sync,
        analysis_id=analysis.id
    )
    
    await db.commit()
    await db.refresh(analysis)
    return ResumeAnalysisResponse(
        success=True,
        data=ResumeAnalysisResponseData.model_validate(analysis)
    )
