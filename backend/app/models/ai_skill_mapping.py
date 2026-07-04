from datetime import datetime
from sqlalchemy import String, DateTime, func, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class AISkillMapping(Base):
    __tablename__ = "ai_skill_mappings"

    raw_skill: Mapped[str] = mapped_column(String(255), primary_key=True)
    normalized: Mapped[str] = mapped_column(String(255), nullable=False)
    canonical: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(255), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
