import uuid
from typing import Dict, Any, List, Optional


class IJobDiscoveryService:
    async def search_jobs(
        self,
        user_id: uuid.UUID,
        query: str,
        location: Optional[str] = None,
        employment_type: Optional[str] = None,
        experience_level: Optional[str] = None,
        salary_min: Optional[int] = None,
        remote_only: bool = False,
        page: int = 1,
        per_page: int = 20,
    ) -> Dict[str, Any]:
        """Tìm kiếm việc làm: ưu tiên cache trong DB (TTL 4h), nếu hết hạn thì gọi
        JSearch API, chuẩn hóa và lưu cache, rồi trả về kèm cờ đã bookmark + phân trang."""
        ...

    async def get_job_details(self, user_id: uuid.UUID, job_id: uuid.UUID) -> Dict[str, Any]:
        """Lấy chi tiết một job, ghi nhận tương tác 'viewed' và trả cờ bookmark."""
        ...

    async def bookmark_job(self, user_id: uuid.UUID, job_id: uuid.UUID) -> bool:
        """Đánh dấu (bookmark) một job."""
        ...

    async def unbookmark_job(self, user_id: uuid.UUID, job_id: uuid.UUID) -> bool:
        """Bỏ đánh dấu một job."""
        ...

    async def get_bookmarks(self, user_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Danh sách các job đã bookmark của người dùng."""
        ...

    async def create_saved_search(
        self, user_id: uuid.UUID, name: str, criteria: Dict[str, Any], alert_frequency: str
    ) -> Dict[str, Any]:
        """Lưu một bộ tiêu chí tìm kiếm để nhận thông báo (alert)."""
        ...

    async def list_saved_searches(self, user_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Liệt kê các tìm kiếm đã lưu."""
        ...

    async def get_recommendations(self, user_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Gợi ý việc làm dựa trên hồ sơ ứng viên."""
        ...
