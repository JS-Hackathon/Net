import uuid
from typing import Dict, Any, List
from app.models.resume_analysis import ResumeAnalysis

class IResumeAnalysisService:
    async def parse_resume_background(
        self, 
        user_id: uuid.UUID, 
        resume_id: uuid.UUID
    ) -> ResumeAnalysis:
        """Kích hoạt tiến trình phân tích CV chạy ngầm. Trích xuất text, gọi Gemini API 
        để lấy JSON cấu trúc, tính điểm tin cậy và lưu kết quả."""
        ...

    async def run_extraction_and_parsing_sync(
        self, 
        analysis_id: uuid.UUID
    ) -> None:
        """Phương thức thực thi đồng bộ quá trình trích xuất và phân tích (chạy trong BackgroundTask)."""
        ...

    async def get_analysis(self, user_id: uuid.UUID, analysis_id: uuid.UUID) -> ResumeAnalysis:
        """Lấy kết quả phân tích CV."""
        ...

    async def get_parsing_status(self, user_id: uuid.UUID, analysis_id: uuid.UUID) -> Dict[str, Any]:
        """Lấy trạng thái tiến trình phân tích để thực hiện polling ở frontend."""
        ...

    async def submit_review(
        self, 
        user_id: uuid.UUID, 
        analysis_id: uuid.UUID, 
        corrections: Dict[str, Any], 
        approved: bool
    ) -> ResumeAnalysis:
        """Phê duyệt hoặc chỉnh sửa kết quả phân tích của AI. 
        Đồng thời đồng bộ hóa kết quả cuối cùng sang CandidateProfile."""
        ...

    async def retry_parsing(self, user_id: uuid.UUID, analysis_id: uuid.UUID) -> ResumeAnalysis:
        """Thử lại quá trình phân tích nếu lần trước bị thất bại."""
        ...
