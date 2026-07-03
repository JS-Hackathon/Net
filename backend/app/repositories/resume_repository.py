import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from app.models.resume import Resume

class ResumeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, resume_id: uuid.UUID) -> Optional[Resume]:
        stmt = select(Resume).where(Resume.id == resume_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: uuid.UUID) -> List[Resume]:
        stmt = select(Resume).where(Resume.user_id == user_id).order_by(Resume.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_primary_by_user_id(self, user_id: uuid.UUID) -> Optional[Resume]:
        stmt = select(Resume).where(Resume.user_id == user_id, Resume.is_primary == True)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def count_by_user_id(self, user_id: uuid.UUID) -> int:
        stmt = select(func.count(Resume.id)).where(Resume.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def create(self, resume: Resume) -> Resume:
        self.db.add(resume)
        await self.db.flush()
        return resume

    async def delete(self, resume: Resume) -> None:
        await self.db.delete(resume)
        await self.db.flush()

    async def unset_primary_for_user(self, user_id: uuid.UUID) -> None:
        stmt = (
            update(Resume)
            .where(Resume.user_id == user_id, Resume.is_primary == True)
            .values(is_primary=False)
        )
        await self.db.execute(stmt)
        await self.db.flush()
