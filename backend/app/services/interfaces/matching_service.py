import uuid
from typing import Dict, Any, List, Optional


class IMatchingService:
    async def calculate_match(self, user_id: uuid.UUID, job_id: uuid.UUID) -> Dict[str, Any]:
        """Tính điểm tương thích giữa hồ sơ ứng viên và một job bằng AI.
        Điểm tổng hợp (overall) được tính có trọng số ở tầng service để đảm bảo ổn định.
        Kết quả được lưu và cache (tái sử dụng nếu hồ sơ/job chưa đổi)."""
        ...

    async def batch_match(self, user_id: uuid.UUID, job_ids: List[uuid.UUID]) -> Dict[str, Any]:
        """Tính match cho nhiều job đồng thời (giới hạn concurrency), tối đa 50 job/lần."""
        ...

    async def auto_match(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """Auto Match một chạm: xếp hạng công ty phù hợp (deterministic, không tốn
        quota AI) + sinh kịch bản phỏng vấn cho công ty đứng đầu bằng 1 call AI."""
        ...

    async def get_match_detail(self, user_id: uuid.UUID, match_id: uuid.UUID) -> Dict[str, Any]:
        """Lấy chi tiết một kết quả match kèm phân tích đầy đủ."""
        ...

    async def get_user_matches(
        self,
        user_id: uuid.UUID,
        min_score: Optional[float] = None,
        sort: str = "score",
        order: str = "desc",
        page: int = 1,
        per_page: int = 20,
    ) -> Dict[str, Any]:
        """Danh sách các match của người dùng, có lọc theo điểm và phân trang."""
        ...

    async def submit_feedback(
        self,
        user_id: uuid.UUID,
        match_id: uuid.UUID,
        feedback_type: Optional[str],
        user_rating: Optional[int],
        feedback_notes: Optional[str],
    ) -> bool:
        """Ghi nhận phản hồi của người dùng về chất lượng match."""
        ...
