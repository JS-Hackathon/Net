import uuid
import hashlib
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.base import ValidationError, NotFoundError
from app.models.resume import Resume
from app.repositories.resume_repository import ResumeRepository
from app.services.interfaces.resume_service import IResumeService
from app.services.interfaces.storage_service import StorageService

class ResumeServiceImpl(IResumeService):
    def __init__(self, db: AsyncSession, storage_service: StorageService):
        self.db = db
        self.repo = ResumeRepository(db)
        self.storage = storage_service
        self.max_file_size = 5 * 1024 * 1024  # 5MB
        self.allowed_extensions = {".pdf", ".docx"}

    async def upload_resume(
        self, 
        user_id: uuid.UUID, 
        file_bytes: bytes, 
        filename: str, 
        content_type: str
    ) -> Resume:
        # Check file size
        if len(file_bytes) > self.max_file_size:
            raise ValidationError("Kích thước file vượt quá giới hạn cho phép (tối đa 5MB)")

        # Validate file extension
        import os
        ext = os.path.splitext(filename)[1].lower()
        if ext not in self.allowed_extensions:
            raise ValidationError("Chỉ hỗ trợ tải lên file định dạng PDF hoặc DOCX")

        # Validate max resumes limit (max 10)
        resumes_count = await self.repo.count_by_user_id(user_id)
        if resumes_count >= 10:
            raise ValidationError("Tài khoản của bạn đã đạt giới hạn tối đa 10 CV. Vui lòng xóa CV cũ trước khi tải lên CV mới.")

        # Compute SHA-256 file hash
        sha256 = hashlib.sha256()
        sha256.update(file_bytes)
        file_hash = sha256.hexdigest()

        # Generate unique path on storage
        unique_filename = f"{user_id}_{uuid.uuid4()}{ext}"
        
        # Upload using StorageService
        stored_path = await self.storage.upload_file(file_bytes, unique_filename)

        # Decide is_primary status
        # If this is the first resume, make it primary automatically
        is_primary = False
        if resumes_count == 0:
            is_primary = True

        # Create Resume entity
        new_resume = Resume(
            user_id=user_id,
            filename=unique_filename,
            original_filename=filename,
            file_path=stored_path,
            file_size=len(file_bytes),
            file_type=ext.replace(".", ""),
            mime_type=content_type,
            file_hash=file_hash,
            upload_status="completed",
            is_primary=is_primary,
            text_extraction_status="pending"
        )

        return await self.repo.create(new_resume)

    async def get_user_resumes(self, user_id: uuid.UUID) -> List[Resume]:
        return await self.repo.get_by_user_id(user_id)

    async def get_resume(self, user_id: uuid.UUID, resume_id: uuid.UUID) -> Resume:
        resume = await self.repo.get_by_id(resume_id)
        if not resume or resume.user_id != user_id:
            raise NotFoundError("Không tìm thấy CV yêu cầu")
        return resume

    async def delete_resume(self, user_id: uuid.UUID, resume_id: uuid.UUID) -> bool:
        resume = await self.repo.get_by_id(resume_id)
        if not resume or resume.user_id != user_id:
            raise NotFoundError("Không tìm thấy CV để xóa")

        is_primary_to_delete = resume.is_primary

        # Delete physical file from storage
        await self.storage.delete_file(resume.filename)

        # Delete database record
        await self.repo.delete(resume)

        # If we deleted the primary resume, make the most recent remaining one primary
        if is_primary_to_delete:
            remaining_resumes = await self.repo.get_by_user_id(user_id)
            if remaining_resumes:
                new_primary = remaining_resumes[0]
                new_primary.is_primary = True
                await self.db.flush()

        return True

    async def set_primary_resume(self, user_id: uuid.UUID, resume_id: uuid.UUID) -> Resume:
        resume = await self.repo.get_by_id(resume_id)
        if not resume or resume.user_id != user_id:
            raise NotFoundError("Không tìm thấy CV yêu cầu")

        # Unset current primary CV
        await self.repo.unset_primary_for_user(user_id)

        # Set new primary CV
        resume.is_primary = True
        await self.db.flush()
        return resume

    async def get_download_url(self, user_id: uuid.UUID, resume_id: uuid.UUID) -> str:
        resume = await self.repo.get_by_id(resume_id)
        if not resume or resume.user_id != user_id:
            raise NotFoundError("Không tìm thấy CV yêu cầu")

        # In R2 storage service implementation, it handles generating download links.
        # If using local storage fallback, it returns the local path '/static/uploads/...'
        # We can directly return the resume's file_path
        return resume.file_path
