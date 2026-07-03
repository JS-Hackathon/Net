import uuid
from typing import Dict, Any, List
from app.models.candidate_profile import CandidateProfile

class ICandidateProfileService:
    async def get_profile(self, user_id: uuid.UUID) -> CandidateProfile:
        """Lấy thông tin hồ sơ ứng viên đầy đủ của người dùng. 
        Nếu chưa tồn tại hồ sơ, tự động tạo hồ sơ trống."""
        ...

    async def update_profile_section(
        self, 
        user_id: uuid.UUID, 
        section: str, 
        data: Dict[str, Any]
    ) -> CandidateProfile:
        """Cập nhật một phân đoạn hồ sơ cụ thể (ví dụ: work_experience, education, personal_info), 
        ghi nhận nhật ký cập nhật (audit log), và cập nhật lại điểm hoàn thiện."""
        ...

    async def get_completeness(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """Tính toán chi tiết điểm hoàn thiện của hồ sơ ứng viên và đưa ra các gợi ý bổ sung."""
        ...

    async def export_profile(self, user_id: uuid.UUID, format: str) -> Dict[str, Any]:
        """Xuất thông tin hồ sơ ứng viên ra định dạng JSON hoặc PDF (đường dẫn tải xuống)."""
        ...
