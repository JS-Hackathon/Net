import uuid
from datetime import datetime
from sqlalchemy import (
    String, DateTime, func, Boolean, ForeignKey, Integer, Text, JSON,
    Numeric, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Job(Base):
    """Cache of job postings sourced from the JSearch API."""
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    external_job_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)  # JSearch API job ID

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    company_logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    job_type: Mapped[str | None] = mapped_column(String(100), nullable=True)          # full-time, part-time, contract, internship
    employment_type: Mapped[str | None] = mapped_column(String(100), nullable=True)   # remote, hybrid, on-site
    experience_level: Mapped[str | None] = mapped_column(String(100), nullable=True)  # entry, mid, senior, executive

    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_currency: Mapped[str] = mapped_column(String(10), default="USD")

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    benefits: Mapped[str | None] = mapped_column(Text, nullable=True)
    skills_required: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # Array of required skills

    industry: Mapped[str | None] = mapped_column(String(255), nullable=True)
    posted_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    application_deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    application_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_platform: Mapped[str | None] = mapped_column(String(100), nullable=True)   # Indeed, LinkedIn, etc.

    # Cache metadata
    cached_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # NOTE: The full-text `search_vector` column (tsvector) is created and maintained
    # entirely at the database level via a trigger defined in the Alembic migration.
    # It is intentionally not mapped here so ORM inserts stay simple; full-text queries
    # reference it through raw SQL in the repository layer.

    # Relationships
    interactions = relationship("UserJobInteraction", back_populates="job", cascade="all, delete-orphan")
    recommendations = relationship("JobRecommendation", back_populates="job", cascade="all, delete-orphan")
    matches = relationship("JobMatch", back_populates="job", cascade="all, delete-orphan")


class UserJobInteraction(Base):
    """Tracks how a user interacts with a job (viewed, bookmarked, applied, rejected)."""
    __tablename__ = "user_job_interactions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    interaction_type: Mapped[str] = mapped_column(String(50), nullable=False)  # viewed, bookmarked, applied, rejected
    interaction_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    job = relationship("Job", back_populates="interactions")

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", "interaction_type", name="uq_user_job_interaction"),
    )


class SavedSearch(Base):
    """A saved job search that can power alerts."""
    __tablename__ = "saved_searches"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    search_criteria: Mapped[dict] = mapped_column(JSON, nullable=False)             # Search parameters
    alert_frequency: Mapped[str] = mapped_column(String(50), default="daily")       # daily, weekly, immediate
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_run: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class JobRecommendation(Base):
    """Cached job recommendations for a user based on their profile."""
    __tablename__ = "job_recommendations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    recommendation_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)  # 0-100
    recommendation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    algorithm_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    job = relationship("Job", back_populates="recommendations")
