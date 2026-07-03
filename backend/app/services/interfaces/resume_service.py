import uuid
from typing import List, Protocol
from app.models.resume import Resume

class IResumeService(Protocol):
    async def upload_resume(
        self, 
        user_id: uuid.UUID, 
        file_bytes: bytes, 
        filename: str, 
        content_type: str
    ) -> Resume:
        """Tải CV lên, kiểm tra kích thước tối đa 5MB và định dạng PDF/DOCX, 
        lưu trữ thông qua StorageService, và ghi nhận thông tin vào database.
        Đồng thời trigger tác vụ chạy ngầm trích xuất văn bản."""
        ...

    async def get_user_resumes(self, user_id: uuid.UUID) -> List[Resume]:
        """Lấy danh sách toàn bộ các CV đã tải lên của người dùng."""
        ...

    async def get_resume(self, user_id: uuid.UUID, resume_id: uuid.UUID) -> Resume:
        """Chi tiết một CV cụ thể của người dùng."""
        ...

    async def delete_resume(self, user_id: uuid.UUID, resume_id: uuid.UUID) -> bool:
        """Xóa CV khỏi hệ thống lưu trữ và cơ sở dữ liệu.
        Nếu CV bị xóa là CV chính (primary), chỉ định một CV khác làm chính."""
        ...

    async def set_primary_resume(self, user_id: uuid.UUID, resume_id: uuid.UUID) -> Resume:
        """Đặt một CV cụ thể làm CV chính (is_primary = True) và bỏ chọn các CV khác."""
        ...

    async def get_download_url(self, user_id: uuid.UUID, resume_id: uuid.UUID) -> str:
        """Lấy đường dẫn tải xuống CV (URL tĩnh nội bộ hoặc signed R2 URL)."""
        ...
