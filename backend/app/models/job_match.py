import uuid
from datetime import datetime
from sqlalchemy import (
    String, DateTime, func, ForeignKey, Integer, Text, JSON,
    Numeric, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class JobMatch(Base):
    """AI-powered compatibility analysis between a candidate and a job."""
    __tablename__ = "job_matches"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    candidate_profile_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=True
    )

    # Match scoring
    overall_match_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)  # 0-100
    skills_match_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    experience_match_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    education_match_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    location_match_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)

    # AI analysis results
    match_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    strengths: Mapped[dict | None] = mapped_column(JSON, nullable=True)                # Array of matching strengths
    weaknesses: Mapped[dict | None] = mapped_column(JSON, nullable=True)               # Array of gaps and weaknesses
    missing_skills: Mapped[dict | None] = mapped_column(JSON, nullable=True)           # Skills required but not possessed
    skill_gaps: Mapped[dict | None] = mapped_column(JSON, nullable=True)               # Detailed skill gap analysis
    improvement_suggestions: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # Recommendations
    recommendation: Mapped[dict | None] = mapped_column(JSON, nullable=True)           # should_apply, likelihood, advice

    # Metadata
    gemini_model_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    matching_algorithm_version: Mapped[str | None] = mapped_column(String(20), nullable=True)
    processing_duration: Mapped[int | None] = mapped_column(Integer, nullable=True)    # Milliseconds
    confidence_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    needs_review: Mapped[bool] = mapped_column(default=False)  # flagged when confidence < 80

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    job = relationship("Job", back_populates="matches")
    skills_matches = relationship("SkillMatch", back_populates="job_match", cascade="all, delete-orphan")
    feedback = relationship("MatchQualityFeedback", back_populates="job_match", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_job_match_user_job"),
    )


class SkillMatch(Base):
    """Per-skill breakdown of a job match."""
    __tablename__ = "skills_matches"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    job_match_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("job_matches.id", ondelete="CASCADE"), nullable=False, index=True
    )
    skill_name: Mapped[str] = mapped_column(String(255), nullable=False)
    skill_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    required_proficiency: Mapped[str | None] = mapped_column(String(50), nullable=True)   # From job requirements
    candidate_proficiency: Mapped[str | None] = mapped_column(String(50), nullable=True)  # From candidate profile
    match_type: Mapped[str | None] = mapped_column(String(50), nullable=True)             # exact, partial, missing, bonus
    match_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)       # 0-100
    importance_weight: Mapped[float | None] = mapped_column(Numeric(3, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    job_match = relationship("JobMatch", back_populates="skills_matches")


class MatchQualityFeedback(Base):
    """User feedback on match quality, used to improve the algorithm."""
    __tablename__ = "match_quality_feedback"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    job_match_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("job_matches.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    feedback_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # applied, interviewed, hired, rejected
    user_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)       # 1-5
    feedback_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    job_match = relationship("JobMatch", back_populates="feedback")

    __table_args__ = (
        CheckConstraint("user_rating >= 1 AND user_rating <= 5", name="ck_match_feedback_rating"),
    )
