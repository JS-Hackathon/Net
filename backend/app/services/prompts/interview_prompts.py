"""Prompt + structured-output schema for the tailored interview scenario used
by the Auto Match feature (one AI call produces a mock-interview script for the
candidate's best-matched company/role)."""

import json
from typing import Dict, Any

INTERVIEW_PROMPT_VERSION = "interview-scenario-1.0"

# Gemini structured-output schema (OpenAPI subset; UPPERCASE types).
INTERVIEW_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "opening": {"type": "STRING", "nullable": True},
        "focus_skills": {"type": "ARRAY", "items": {"type": "STRING"}},
        "gaps_to_prepare": {"type": "ARRAY", "items": {"type": "STRING"}},
        "questions": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "category": {"type": "STRING", "nullable": True},   # behavioral | technical | role | culture
                    "question": {"type": "STRING", "nullable": True},
                    "assesses": {"type": "STRING", "nullable": True},
                    "answer_tip": {"type": "STRING", "nullable": True},
                },
            },
        },
        "preparation_tips": {"type": "ARRAY", "items": {"type": "STRING"}},
        "closing": {"type": "STRING", "nullable": True},
    },
    "required": ["questions"],
}


def build_interview_prompt(profile: Dict[str, Any], job: Dict[str, Any]) -> str:
    """Compose the interview-scenario prompt from a candidate profile + a job."""
    return (
        "Bạn là chuyên gia tuyển dụng. Dựa trên HỒ SƠ ỨNG VIÊN và TIN TUYỂN DỤNG bên dưới, "
        "hãy soạn một KỊCH BẢN PHỎNG VẤN THỬ phù hợp để ứng viên luyện tập cho đúng vị trí này.\n"
        "Yêu cầu:\n"
        "- Viết hoàn toàn bằng TIẾNG VIỆT.\n"
        "- 6–8 câu hỏi trải đều các nhóm: behavioral, technical, role, culture "
        "(gán vào trường category).\n"
        "- Câu technical phải bám sát kỹ năng/yêu cầu của tin tuyển dụng.\n"
        "- `focus_skills`: kỹ năng ứng viên nên nhấn mạnh (phần khớp). "
        "`gaps_to_prepare`: điểm ứng viên còn yếu so với yêu cầu, cần chuẩn bị.\n"
        "- Mỗi câu hỏi kèm `assesses` (đánh giá điều gì) và `answer_tip` (gợi ý trả lời).\n"
        "- KHÔNG bịa thông tin không có trong hồ sơ.\n\n"
        f"HỒ SƠ ỨNG VIÊN:\n{json.dumps(profile, ensure_ascii=False)}\n\n"
        f"TIN TUYỂN DỤNG:\n{json.dumps(job, ensure_ascii=False)}"
    )
