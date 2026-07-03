from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_candidate_profile_service
from app.models.user import User
from app.schemas.candidate_profile import (
    CandidateProfileResponse,
    CandidateProfileResponseData,
    ProfileSectionUpdateRequest,
    ProfileCompletenessResponse,
    ProfileCompletenessResponseData,
    ProfileExportRequest,
    ProfileExportResponse,
    ProfileExportResponseData
)
from app.services.interfaces.candidate_profile_service import ICandidateProfileService

router = APIRouter(
    prefix="/profile",
    tags=["Candidate Profile - Quản lý hồ sơ ứng viên"]
)

@router.get(
    "",
    response_model=CandidateProfileResponse,
    summary="Lấy thông tin hồ sơ ứng viên",
    description="Truy xuất toàn bộ hồ sơ ứng viên chi tiết (bao gồm cả lịch sử làm việc, học tập, kỹ năng,...)."
)
async def get_profile(
    current_user: User = Depends(get_current_user),
    profile_service: ICandidateProfileService = Depends(get_candidate_profile_service)
) -> CandidateProfileResponse:
    profile = await profile_service.get_profile(user_id=current_user.id)
    return CandidateProfileResponse(
        success=True,
        data=CandidateProfileResponseData.model_validate(profile)
    )

@router.put(
    "",
    response_model=CandidateProfileResponse,
    summary="Cập nhật phân đoạn hồ sơ ứng viên",
    description="Cập nhật một mục cụ thể trong hồ sơ ứng viên (ví dụ: học vấn, kỹ năng, kinh nghiệm) và tự động tính toán lại điểm hoàn thiện."
)
async def update_profile_section(
    payload: ProfileSectionUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    profile_service: ICandidateProfileService = Depends(get_candidate_profile_service)
) -> CandidateProfileResponse:
    profile = await profile_service.update_profile_section(
        user_id=current_user.id,
        section=payload.section,
        data=payload.data
    )
    await db.commit()
    await db.refresh(profile)
    return CandidateProfileResponse(
        success=True,
        data=CandidateProfileResponseData.model_validate(profile)
    )

@router.get(
    "/completeness",
    response_model=ProfileCompletenessResponse,
    summary="Lấy chi tiết điểm hoàn thiện hồ sơ",
    description="Truy xuất chi tiết điểm hoàn thiện của từng phân đoạn hồ sơ kèm theo gợi ý tối ưu hồ sơ."
)
async def get_completeness(
    current_user: User = Depends(get_current_user),
    profile_service: ICandidateProfileService = Depends(get_candidate_profile_service)
) -> ProfileCompletenessResponse:
    completeness_data = await profile_service.get_completeness(user_id=current_user.id)
    return ProfileCompletenessResponse(
        success=True,
        data=ProfileCompletenessResponseData(**completeness_data)
    )

@router.post(
    "/export",
    response_model=ProfileExportResponse,
    summary="Xuất file hồ sơ cá nhân",
    description="Yêu cầu xuất thông tin hồ sơ ra định dạng PDF hoặc JSON để tải về."
)
async def export_profile(
    payload: ProfileExportRequest,
    current_user: User = Depends(get_current_user),
    profile_service: ICandidateProfileService = Depends(get_candidate_profile_service)
) -> ProfileExportResponse:
    export_data = await profile_service.export_profile(
        user_id=current_user.id,
        format=payload.format
    )
    return ProfileExportResponse(
        success=True,
        data=ProfileExportResponseData(**export_data)
    )
