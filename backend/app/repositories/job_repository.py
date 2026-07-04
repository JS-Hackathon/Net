import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, and_, or_, desc
from app.models.job import Job, UserJobInteraction, SavedSearch, JobRecommendation


class JobRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ------------------------------------------------------------------ jobs
    async def get_by_id(self, job_id: uuid.UUID) -> Optional[Job]:
        stmt = select(Job).where(Job.id == job_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_external_id(self, external_job_id: str) -> Optional[Job]:
        stmt = select(Job).where(Job.external_job_id == external_job_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_job(self, data: Dict[str, Any]) -> Job:
        """Insert a job or update the existing row keyed by external_job_id."""
        existing = await self.get_by_external_id(data["external_job_id"])
        if existing:
            for key, value in data.items():
                if key == "external_job_id":
                    continue
                setattr(existing, key, value)
            await self.db.flush()
            return existing

        job = Job(**data)
        self.db.add(job)
        await self.db.flush()
        return job

    async def search(
        self,
        *,
        query: Optional[str] = None,
        location: Optional[str] = None,
        employment_type: Optional[str] = None,
        experience_level: Optional[str] = None,
        salary_min: Optional[int] = None,
        remote_only: bool = False,
        page: int = 1,
        per_page: int = 20,
    ) -> Tuple[List[Job], int]:
        """Search cached jobs with filters and pagination. Returns (jobs, total)."""
        conditions = [Job.is_active.is_(True)]

        if location:
            conditions.append(Job.location.ilike(f"%{location}%"))
        if employment_type:
            conditions.append(Job.employment_type == employment_type)
        if experience_level:
            conditions.append(Job.experience_level == experience_level)
        if salary_min is not None:
            conditions.append(Job.salary_max >= salary_min)
        if remote_only:
            conditions.append(Job.employment_type == "remote")

        base = select(Job).where(and_(*conditions))
        count_stmt = select(func.count()).select_from(Job).where(and_(*conditions))

        if query:
            # Keyword search across key fields using ILIKE (case-insensitive).
            # search_vector column does not exist; use ILIKE as a pragmatic fallback.
            keywords = [kw.strip() for kw in query.replace(",", " ").split() if kw.strip()]
            keyword_conditions = []
            for kw in keywords:
                pattern = f"%{kw}%"
                keyword_conditions.append(Job.title.ilike(pattern))
                keyword_conditions.append(Job.company_name.ilike(pattern))
                keyword_conditions.append(Job.description.ilike(pattern))
                keyword_conditions.append(Job.location.ilike(pattern))
            if keyword_conditions:
                kw_filter = or_(*keyword_conditions)
                base = base.where(kw_filter)
                count_stmt = count_stmt.where(kw_filter)

        # Cap result window for performance (BR: max 1000 jobs per query).
        offset = max(0, (page - 1) * per_page)
        base = base.order_by(desc(Job.posted_date)).offset(offset).limit(min(per_page, 100))

        total_result = await self.db.execute(count_stmt)
        total = min(total_result.scalar_one(), 1000)

        result = await self.db.execute(base)
        return list(result.scalars().all()), total

    async def deactivate_expired(self) -> None:
        """Mark cached jobs whose TTL has elapsed as inactive."""
        now = datetime.now(timezone.utc)
        stmt = (
            select(Job)
            .where(Job.is_active.is_(True), Job.expires_at.is_not(None), Job.expires_at < now)
        )
        result = await self.db.execute(stmt)
        for job in result.scalars().all():
            job.is_active = False
        await self.db.flush()

    # ------------------------------------------------------ interactions
    async def get_interaction(
        self, user_id: uuid.UUID, job_id: uuid.UUID, interaction_type: str
    ) -> Optional[UserJobInteraction]:
        stmt = select(UserJobInteraction).where(
            UserJobInteraction.user_id == user_id,
            UserJobInteraction.job_id == job_id,
            UserJobInteraction.interaction_type == interaction_type,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def add_interaction(
        self,
        user_id: uuid.UUID,
        job_id: uuid.UUID,
        interaction_type: str,
        interaction_data: Optional[Dict[str, Any]] = None,
    ) -> UserJobInteraction:
        """Create the interaction if it does not exist (idempotent per unique key)."""
        existing = await self.get_interaction(user_id, job_id, interaction_type)
        if existing:
            if interaction_data is not None:
                existing.interaction_data = interaction_data
            await self.db.flush()
            return existing

        interaction = UserJobInteraction(
            user_id=user_id,
            job_id=job_id,
            interaction_type=interaction_type,
            interaction_data=interaction_data,
        )
        self.db.add(interaction)
        await self.db.flush()
        return interaction

    async def remove_interaction(
        self, user_id: uuid.UUID, job_id: uuid.UUID, interaction_type: str
    ) -> None:
        stmt = delete(UserJobInteraction).where(
            UserJobInteraction.user_id == user_id,
            UserJobInteraction.job_id == job_id,
            UserJobInteraction.interaction_type == interaction_type,
        )
        await self.db.execute(stmt)
        await self.db.flush()

    async def get_bookmarked_job_ids(self, user_id: uuid.UUID) -> set[uuid.UUID]:
        stmt = select(UserJobInteraction.job_id).where(
            UserJobInteraction.user_id == user_id,
            UserJobInteraction.interaction_type == "bookmarked",
        )
        result = await self.db.execute(stmt)
        return set(result.scalars().all())

    async def get_bookmarks(self, user_id: uuid.UUID) -> List[Tuple[Job, datetime]]:
        stmt = (
            select(Job, UserJobInteraction.created_at)
            .join(UserJobInteraction, UserJobInteraction.job_id == Job.id)
            .where(
                UserJobInteraction.user_id == user_id,
                UserJobInteraction.interaction_type == "bookmarked",
            )
            .order_by(desc(UserJobInteraction.created_at))
        )
        result = await self.db.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]

    # ------------------------------------------------------ saved searches
    async def create_saved_search(self, saved_search: SavedSearch) -> SavedSearch:
        self.db.add(saved_search)
        await self.db.flush()
        return saved_search

    async def list_saved_searches(self, user_id: uuid.UUID) -> List[SavedSearch]:
        stmt = (
            select(SavedSearch)
            .where(SavedSearch.user_id == user_id, SavedSearch.is_active.is_(True))
            .order_by(desc(SavedSearch.created_at))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_saved_search(self, search_id: uuid.UUID) -> Optional[SavedSearch]:
        stmt = select(SavedSearch).where(SavedSearch.id == search_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # ------------------------------------------------------ recommendations
    async def replace_recommendations(
        self, user_id: uuid.UUID, records: List[JobRecommendation]
    ) -> List[JobRecommendation]:
        await self.db.execute(
            delete(JobRecommendation).where(JobRecommendation.user_id == user_id)
        )
        for r in records:
            self.db.add(r)
        await self.db.flush()
        return records

    async def get_recommendations(self, user_id: uuid.UUID) -> List[Tuple[JobRecommendation, Job]]:
        stmt = (
            select(JobRecommendation, Job)
            .join(Job, Job.id == JobRecommendation.job_id)
            .where(JobRecommendation.user_id == user_id)
            .order_by(desc(JobRecommendation.recommendation_score))
        )
        result = await self.db.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]
