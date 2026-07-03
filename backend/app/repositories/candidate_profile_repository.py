import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from app.models.candidate_profile import CandidateProfile, ProfileCompleteness, ProfileUpdate

class CandidateProfileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, profile_id: uuid.UUID) -> Optional[CandidateProfile]:
        stmt = select(CandidateProfile).where(CandidateProfile.id == profile_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: uuid.UUID) -> Optional[CandidateProfile]:
        stmt = select(CandidateProfile).where(CandidateProfile.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, profile: CandidateProfile) -> CandidateProfile:
        self.db.add(profile)
        await self.db.flush()
        return profile

    async def get_completeness_by_profile_id(self, profile_id: uuid.UUID) -> List[ProfileCompleteness]:
        stmt = select(ProfileCompleteness).where(ProfileCompleteness.profile_id == profile_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_or_update_completeness(self, completeness_record: ProfileCompleteness) -> ProfileCompleteness:
        # Check if record already exists for this section and profile
        stmt = select(ProfileCompleteness).where(
            ProfileCompleteness.profile_id == completeness_record.profile_id,
            ProfileCompleteness.section_name == completeness_record.section_name
        )
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.completeness_percentage = completeness_record.completeness_percentage
            existing.missing_fields = completeness_record.missing_fields
            existing.suggestions = completeness_record.suggestions
            existing.updated_at = func.now() if hasattr(func, 'now') else datetime.utcnow()
            await self.db.flush()
            return existing
        else:
            self.db.add(completeness_record)
            await self.db.flush()
            return completeness_record

    async def delete_completeness_records(self, profile_id: uuid.UUID) -> None:
        stmt = delete(ProfileCompleteness).where(ProfileCompleteness.profile_id == profile_id)
        await self.db.execute(stmt)
        await self.db.flush()

    async def create_update_log(self, update_log: ProfileUpdate) -> ProfileUpdate:
        self.db.add(update_log)
        await self.db.flush()
        return update_log
