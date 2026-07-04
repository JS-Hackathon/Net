import uuid
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, desc, asc, func
from app.models.job_match import JobMatch, SkillMatch, MatchQualityFeedback
from app.models.job import Job


class JobMatchRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, match_id: uuid.UUID) -> Optional[JobMatch]:
        stmt = select(JobMatch).where(JobMatch.id == match_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_and_job(
        self, user_id: uuid.UUID, job_id: uuid.UUID
    ) -> Optional[JobMatch]:
        stmt = select(JobMatch).where(
            JobMatch.user_id == user_id, JobMatch.job_id == job_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_match(self, user_id: uuid.UUID, job_id: uuid.UUID, values: dict) -> JobMatch:
        """Create or update the single match per (user, job)."""
        existing = await self.get_by_user_and_job(user_id, job_id)
        if existing:
            for key, value in values.items():
                setattr(existing, key, value)
            # Clear stale per-skill breakdown; it is regenerated on each match.
            await self.db.execute(
                delete(SkillMatch).where(SkillMatch.job_match_id == existing.id)
            )
            await self.db.flush()
            return existing

        match = JobMatch(user_id=user_id, job_id=job_id, **values)
        self.db.add(match)
        await self.db.flush()
        return match

    async def add_skill_match(self, skill_match: SkillMatch) -> SkillMatch:
        self.db.add(skill_match)
        await self.db.flush()
        return skill_match

    async def get_skill_matches(self, job_match_id: uuid.UUID) -> List[SkillMatch]:
        stmt = select(SkillMatch).where(SkillMatch.job_match_id == job_match_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_matches(
        self,
        user_id: uuid.UUID,
        min_score: Optional[float] = None,
        sort: str = "score",
        order: str = "desc",
        page: int = 1,
        per_page: int = 20,
    ) -> Tuple[List[Tuple[JobMatch, Job]], int]:
        conditions = [JobMatch.user_id == user_id]
        if min_score is not None:
            conditions.append(JobMatch.overall_match_score >= min_score)

        sort_col = JobMatch.overall_match_score if sort == "score" else JobMatch.created_at
        direction = desc if order == "desc" else asc

        count_stmt = select(func.count()).select_from(JobMatch).where(*conditions)
        total = (await self.db.execute(count_stmt)).scalar_one()

        offset = max(0, (page - 1) * per_page)
        stmt = (
            select(JobMatch, Job)
            .join(Job, Job.id == JobMatch.job_id)
            .where(*conditions)
            .order_by(direction(sort_col))
            .offset(offset)
            .limit(per_page)
        )
        result = await self.db.execute(stmt)
        rows = [(row[0], row[1]) for row in result.all()]
        return rows, total

    async def add_feedback(self, feedback: MatchQualityFeedback) -> MatchQualityFeedback:
        self.db.add(feedback)
        await self.db.flush()
        return feedback
