from app.services.interfaces.ai_provider import AIProvider
from app.services.impl.gemini_provider import GeminiProvider
from app.services.interfaces.jsearch_service import JSearchService
from app.services.impl.jsearch_service_impl import JSearchServiceImpl
from app.services.interfaces.storage_service import StorageService
from app.services.impl.r2_storage_service import R2StorageService

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.database import get_db
from app.services.interfaces.auth_service import IAuthService
from app.services.impl.auth_service_impl import AuthServiceImpl

# Singletons or instantiation functions
_ai_provider = GeminiProvider()
_jsearch_service = JSearchServiceImpl()
_storage_service = R2StorageService()

from app.services.interfaces.resume_service import IResumeService
from app.services.impl.resume_service_impl import ResumeServiceImpl
from app.services.interfaces.resume_analysis_service import IResumeAnalysisService
from app.services.impl.resume_analysis_service_impl import ResumeAnalysisServiceImpl
from app.services.interfaces.candidate_profile_service import ICandidateProfileService
from app.services.impl.candidate_profile_service_impl import CandidateProfileServiceImpl
from app.services.interfaces.job_discovery_service import IJobDiscoveryService
from app.services.impl.job_discovery_service_impl import JobDiscoveryServiceImpl
from app.services.interfaces.matching_service import IMatchingService
from app.services.impl.matching_service_impl import MatchingServiceImpl

from app.services.interfaces.skill_normalizer_service import ISkillNormalizerService
from app.services.impl.skill_normalizer_service_impl import SkillNormalizerServiceImpl
from app.services.interfaces.confidence_engine_service import IConfidenceEngineService
from app.services.impl.confidence_engine_service_impl import ConfidenceEngineServiceImpl
from app.services.interfaces.job_matching_service import IJobMatchingService
from app.services.impl.job_matching_service_impl import JobMatchingServiceImpl


def get_ai_provider() -> AIProvider:
    return _ai_provider

def get_jsearch_service() -> JSearchService:
    return _jsearch_service

def get_storage_service() -> StorageService:
    return _storage_service

def get_auth_service(db: AsyncSession = Depends(get_db)) -> IAuthService:
    return AuthServiceImpl(db)

def get_resume_service(
    db: AsyncSession = Depends(get_db),
    storage = Depends(get_storage_service)
) -> IResumeService:
    return ResumeServiceImpl(db, storage)

def get_resume_analysis_service(
    db: AsyncSession = Depends(get_db),
    storage = Depends(get_storage_service),
    ai = Depends(get_ai_provider)
) -> IResumeAnalysisService:
    return ResumeAnalysisServiceImpl(db, storage, ai)

def get_candidate_profile_service(
    db: AsyncSession = Depends(get_db)
) -> ICandidateProfileService:
    return CandidateProfileServiceImpl(db)

def get_skill_normalizer_service(
    db: AsyncSession = Depends(get_db)
) -> ISkillNormalizerService:
    return SkillNormalizerServiceImpl(db)

def get_confidence_engine_service() -> IConfidenceEngineService:
    return ConfidenceEngineServiceImpl()

def get_job_matching_service(
    skill_normalizer: ISkillNormalizerService = Depends(get_skill_normalizer_service),
    confidence_engine: IConfidenceEngineService = Depends(get_confidence_engine_service)
) -> IJobMatchingService:
    return JobMatchingServiceImpl(skill_normalizer, confidence_engine)


def get_job_discovery_service(
    db: AsyncSession = Depends(get_db),
    jsearch = Depends(get_jsearch_service)
) -> IJobDiscoveryService:
    return JobDiscoveryServiceImpl(db, jsearch)

def get_matching_service(
    db: AsyncSession = Depends(get_db),
    ai = Depends(get_ai_provider)
) -> IMatchingService:
    return MatchingServiceImpl(db, ai)


import uuid
from fastapi import HTTPException, status
from app.core.security import get_current_user_claims
from sqlalchemy import select
from app.models.user import User

async def get_current_user(
    claims: dict = Depends(get_current_user_claims),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency to retrieve the currently authenticated user from database."""
    user_id_str = claims.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Không tìm thấy thông tin người dùng trong token"
        )
    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Mã định danh người dùng không đúng định dạng"
        )
        
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Tài khoản không tồn tại"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Tài khoản đã bị khóa"
        )
        
    return user
