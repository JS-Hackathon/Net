import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, func, Boolean, ForeignKey, Integer, Text, JSON, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    resume_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, processing, completed, failed, reviewing
    confidence_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)  # overall confidence 0-100
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    gemini_response_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    parsing_duration: Mapped[int | None] = mapped_column(Integer, nullable=True)  # in milliseconds
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    resume = relationship("Resume", back_populates="analyses")
    user = relationship("User", foreign_keys=[user_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    metrics = relationship("ParsingMetric", back_populates="analysis", cascade="all, delete-orphan")
    profile = relationship("CandidateProfile", back_populates="source_analysis", uselist=False)

class ParsingMetric(Base):
    __tablename__ = "parsing_metrics"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    analysis_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("resume_analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    extraction_method: Mapped[str] = mapped_column(String(50), nullable=False)  # ai_primary, ai_fallback, manual
    validation_status: Mapped[str] = mapped_column(String(50), nullable=False)  # valid, invalid, needs_review
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    analysis = relationship("ResumeAnalysis", back_populates="metrics")

class AIPrompt(Base):
    __tablename__ = "ai_prompts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False)
    schema_version: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("name", "version", name="uq_ai_prompts_name_version"),
    )
