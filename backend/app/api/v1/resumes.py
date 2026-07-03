from fastapi import APIRouter, Depends, Request, status, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_resume_service, get_resume_analysis_service
from app.models.user import User
from app.schemas.resume import (
    ResumeResponse, 
    ResumeListResponse, 
    ResumeListResponseData,
    ResumeResponseData,
    ResumeDownloadResponse,
    ResumeDownloadResponseData
)
from app.services.interfaces.resume_service import IResumeService
from app.services.interfaces.resume_analysis_service import IResumeAnalysisService

router = APIRouter(
    prefix="/resumes",
    tags=["Resume Management - Hệ thống quản lý CV"]
)

@router.post(
    "/upload",
    response_model=ResumeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tải lên CV mới",
    description="Tải lên CV (định dạng PDF/DOCX, tối đa 5MB) và tự động kích hoạt quá trình phân tích CV bằng AI chạy ngầm."
)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="File CV (PDF hoặc DOCX)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    resume_service: IResumeService = Depends(get_resume_service),
    analysis_service: IResumeAnalysisService = Depends(get_resume_analysis_service)
) -> ResumeResponse:
    # 1. Read file bytes
    file_bytes = await file.read()
    
    # 2. Upload file & log meta
    resume = await resume_service.upload_resume(
        user_id=current_user.id,
        file_bytes=file_bytes,
        filename=file.filename,
        content_type=file.content_type
    )
    
    # 3. Create analysis entry (status = pending)
    analysis = await analysis_service.parse_resume_background(
        user_id=current_user.id,
        resume_id=resume.id
    )
    
    # 4. Add extraction and parsing to background tasks
    background_tasks.add_task(
        analysis_service.run_extraction_and_parsing_sync,
        analysis_id=analysis.id
    )
    
    await db.commit()
    
    # Refresh to load updated_at and relations properly
    await db.refresh(resume)
    
    return ResumeResponse(
        success=True,
        data=ResumeResponseData.model_validate(resume)
    )

@router.get(
    "",
    response_model=ResumeListResponse,
    summary="Danh sách CV của người dùng",
    description="Lấy danh sách tất cả các CV mà người dùng hiện tại đã tải lên."
)
async def list_resumes(
    current_user: User = Depends(get_current_user),
    resume_service: IResumeService = Depends(get_resume_service)
) -> ResumeListResponse:
    resumes = await resume_service.get_user_resumes(user_id=current_user.id)
    
    response_data = ResumeListResponseData(
        resumes=[ResumeResponseData.model_validate(r) for r in resumes],
        total=len(resumes)
    )
    
    return ResumeListResponse(
        success=True,
        data=response_data
    )

@router.get(
    "/{resume_id}",
    response_model=ResumeResponse,
    summary="Chi tiết một CV",
    description="Xem thông tin chi tiết và trạng thái của một CV cụ thể."
)
async def get_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    resume_service: IResumeService = Depends(get_resume_service)
) -> ResumeResponse:
    resume = await resume_service.get_resume(
        user_id=current_user.id,
        resume_id=uuid.UUID(resume_id)
    )
    return ResumeResponse(
        success=True,
        data=ResumeResponseData.model_validate(resume)
    )

@router.delete(
    "/{resume_id}",
    summary="Xóa CV",
    description="Xóa một CV cụ thể khỏi hệ thống lưu trữ và cơ sở dữ liệu."
)
async def delete_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    resume_service: IResumeService = Depends(get_resume_service)
):
    await resume_service.delete_resume(
        user_id=current_user.id,
        resume_id=uuid.UUID(resume_id)
    )
    await db.commit()
    return {"success": True, "message": "Xóa CV thành công"}

@router.put(
    "/{resume_id}/primary",
    response_model=ResumeResponse,
    summary="Đặt làm CV chính",
    description="Thiết lập CV này làm CV chính được sử dụng mặc định trong hệ thống."
)
async def set_primary(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    resume_service: IResumeService = Depends(get_resume_service)
) -> ResumeResponse:
    resume = await resume_service.set_primary_resume(
        user_id=current_user.id,
        resume_id=uuid.UUID(resume_id)
    )
    await db.commit()
    return ResumeResponse(
        success=True,
        data=ResumeResponseData.model_validate(resume)
    )

@router.get(
    "/{resume_id}/download",
    response_model=ResumeDownloadResponse,
    summary="Lấy đường dẫn tải xuống CV",
    description="Lấy liên kết tải xuống file CV gốc có thời hạn sử dụng bảo mật."
)
async def get_download_url(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    resume_service: IResumeService = Depends(get_resume_service)
) -> ResumeDownloadResponse:
    download_url = await resume_service.get_download_url(
        user_id=current_user.id,
        resume_id=uuid.UUID(resume_id)
    )
    
    return ResumeDownloadResponse(
        success=True,
        data=ResumeDownloadResponseData(
            download_url=download_url,
            expires_at=None  # Local fallback download has no expiry
        )
    )
import uuid
