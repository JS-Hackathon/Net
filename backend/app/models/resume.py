import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, func, Boolean, ForeignKey, Integer, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    upload_status: Mapped[str] = mapped_column(String(20), default="uploading")  # uploading, completed, failed, processing
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    text_extraction_status: Mapped[str | None] = mapped_column(String(20), default="pending")  # pending, completed, failed
    metadata_info: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # renamed from metadata to avoid SQLAlchemy conflicts
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="resumes")
    analyses = relationship("ResumeAnalysis", back_populates="resume", cascade="all, delete-orphan")
