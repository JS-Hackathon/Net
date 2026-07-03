import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.resume_analysis import ResumeAnalysis, ParsingMetric, AIPrompt

class ResumeAnalysisRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, analysis_id: uuid.UUID) -> Optional[ResumeAnalysis]:
        stmt = select(ResumeAnalysis).where(ResumeAnalysis.id == analysis_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_resume_id(self, resume_id: uuid.UUID) -> List[ResumeAnalysis]:
        stmt = select(ResumeAnalysis).where(ResumeAnalysis.resume_id == resume_id).order_by(ResumeAnalysis.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_completed_by_user_id(self, user_id: uuid.UUID) -> Optional[ResumeAnalysis]:
        stmt = (
            select(ResumeAnalysis)
            .where(ResumeAnalysis.user_id == user_id, ResumeAnalysis.status == "completed")
            .order_by(desc(ResumeAnalysis.completed_at))
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, analysis: ResumeAnalysis) -> ResumeAnalysis:
        self.db.add(analysis)
        await self.db.flush()
        return analysis

    async def create_metric(self, metric: ParsingMetric) -> ParsingMetric:
        self.db.add(metric)
        await self.db.flush()
        return metric

    async def get_active_prompt(self, name: str) -> Optional[AIPrompt]:
        stmt = select(AIPrompt).where(AIPrompt.name == name, AIPrompt.is_active == True)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
