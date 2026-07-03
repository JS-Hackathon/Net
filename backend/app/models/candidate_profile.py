import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, func, Boolean, ForeignKey, Integer, Text, JSON, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    source_analysis_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("resume_analyses.id", ondelete="SET NULL"), nullable=True)

    # Personal Information
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    portfolio_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    github_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    website_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Professional Summary
    professional_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    career_objective: Mapped[str | None] = mapped_column(Text, nullable=True)
    years_of_experience: Mapped[int | None] = mapped_column(Integer, nullable=True)
    current_role: Mapped[str | None] = mapped_column(String(255), nullable=True)
    current_company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    salary_expectation_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_expectation_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    availability: Mapped[str | None] = mapped_column(String(50), nullable=True)  # immediate, 2_weeks, 1_month, etc.

    # Structured Data (JSON)
    work_experience: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # Array of work experience objects
    education: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # Array of education objects
    technical_skills: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # Array of technical skills with categories
    soft_skills: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # Array of soft skills
    certifications: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # Array of certifications
    languages: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # Array of languages with proficiency
    projects: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # Array of projects
    achievements: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # Array of achievements and awards

    # Profile Metadata
    completeness_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0.00)  # 0-100
    last_updated_section: Mapped[str | None] = mapped_column(String(100), nullable=True)
    profile_strength: Mapped[str] = mapped_column(String(20), default="basic")  # basic, good, strong, excellent
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    is_searchable: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    last_viewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="profile")
    source_analysis = relationship("ResumeAnalysis", back_populates="profile")
    completeness_records = relationship("ProfileCompleteness", back_populates="profile", cascade="all, delete-orphan")
    updates = relationship("ProfileUpdate", back_populates="profile", cascade="all, delete-orphan")

class ProfileCompleteness(Base):
    __tablename__ = "profile_completeness"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    section_name: Mapped[str] = mapped_column(String(100), nullable=False)
    completeness_percentage: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    missing_fields: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # Array of missing field names
    suggestions: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # Array of suggestions
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )

    # Relationships
    profile = relationship("CandidateProfile", back_populates="completeness_records")

class ProfileUpdate(Base):
    __tablename__ = "profile_updates"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    section_name: Mapped[str] = mapped_column(String(100), nullable=False)
    field_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    old_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    update_source: Mapped[str] = mapped_column(String(50), default="manual")  # manual, ai_parsing, import, sync
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    profile = relationship("CandidateProfile", back_populates="updates")
    user = relationship("User")
