import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.resume import Resume
from app.models.candidate_profile import CandidateProfile

pytestmark = pytest.mark.asyncio

async def test_resume_upload_parsing_profile_flow(
    client: AsyncClient, 
    db_session: AsyncSession, 
    monkeypatch
):
    # Mock TextExtractor to return a fixed string instead of parsing invalid pdf bytes
    monkeypatch.setattr(
        "app.services.impl.resume_analysis_service_impl.TextExtractor.extract_text",
        lambda file_bytes, file_type: "Nguyen Van A resume content"
    )

    # Async mock for GeminiProvider.parse_resume
    async def mock_parse_resume(self, text: str):
        return {
            "personal_info": {
                "full_name": "Nguyễn Văn A",
                "email": "candidate@example.com",
                "phone": "0987654321",
                "location": "Hà Nội, Việt Nam",
                "linkedin_url": "https://linkedin.com/in/nguyenvana",
                "github_url": "https://github.com/nguyenvana",
                "portfolio_url": None,
                "website_url": None
            },
            "professional_summary": "Lập trình viên Full Stack Junior với niềm đam mê xây dựng các sản phẩm web chất lượng cao, tối ưu hiệu năng. Có thế mạnh về xây dựng RESTful API bằng Python/FastAPI và giao diện người dùng trực quan bằng React/TypeScript.",
            "career_objective": "Trở thành Kỹ sư phần mềm chuyên nghiệp, đóng góp vào sự phát triển của các sản phẩm AI đột phá.",
            "years_of_experience": 1,
            "skills": ["Python", "FastAPI", "React", "TypeScript", "SQL", "Docker", "Git", "TailwindCSS"],
            "education": [
                {
                    "degree": "Kỹ sư Khoa học Máy tính",
                    "institution": "Đại học FPT",
                    "graduation_year": "2026",
                    "gpa": "3.6/4.0"
                }
            ],
            "experience": [
                {
                    "title": "Software Engineering Intern",
                    "company": "Tech Corp",
                    "duration": "6 months",
                    "responsibilities": [
                        "Xây dựng và tối ưu hóa các RESTful API sử dụng FastAPI",
                        "Thiết kế giao diện người dùng động với React.js và TailwindCSS",
                        "Viết unit test bảo đảm chất lượng code đạt trên 80%"
                    ]
                }
            ],
            "projects": [
                {
                    "name": "MockAI Career Copilot",
                    "description": "Nền tảng chuẩn bị phỏng vấn thông minh tích hợp AI hỗ trợ ứng viên rèn luyện kỹ năng và tối ưu CV."
                }
            ],
            "certifications": ["AWS Certified Cloud Practitioner", "Google IT Support Professional Certificate"]
        }

    # Mock GeminiProvider.parse_resume to return a fixed structure deterministically
    monkeypatch.setattr(
        "app.services.impl.gemini_provider.GeminiProvider.parse_resume",
        mock_parse_resume
    )

    # 1. Register a test candidate
    register_data = {
        "email": "candidate_test@example.com",
        "password": "Password123!",
        "full_name": "Nguyen Van A",
        "terms_accepted": True
    }
    reg_resp = await client.post("/api/v1/auth/register", json=register_data)
    assert reg_resp.status_code == 201
    access_token = reg_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 2. Upload a mock resume file
    pdf_bytes = b"%PDF-1.4 mock pdf content"
    files = {"file": ("my_resume.pdf", pdf_bytes, "application/pdf")}
    
    upload_resp = await client.post("/api/v1/resumes/upload", files=files, headers=headers)
    assert upload_resp.status_code == 201
    
    upload_data = upload_resp.json()
    assert upload_data["success"] is True
    resume_id = upload_data["data"]["id"]
    assert upload_data["data"]["original_filename"] == "my_resume.pdf"
    assert upload_data["data"]["file_type"] == "pdf"

    # 3. Retrieve list of resumes
    list_resp = await client.get("/api/v1/resumes", headers=headers)
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert list_data["success"] is True
    assert list_data["data"]["total"] == 1
    assert list_data["data"]["resumes"][0]["id"] == resume_id

    # 4. Check that background parsing succeeded
    # We trigger a manual parse to explicitly return the analysis ID and process it
    parse_resp = await client.post(f"/api/v1/resumes/{resume_id}/parse", headers=headers)
    assert parse_resp.status_code == 201
    parse_data = parse_resp.json()
    analysis_id = parse_data["data"]["id"]
    assert parse_data["data"]["status"] in ("pending", "processing", "completed", "reviewing")

    # 5. Check parsing status
    status_resp = await client.get(f"/api/v1/analyses/{analysis_id}/status", headers=headers)
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert "status" in status_data["data"]

    # 6. Fetch the candidate profile (created or default)
    profile_resp = await client.get("/api/v1/profile", headers=headers)
    assert profile_resp.status_code == 200
    profile_data = profile_resp.json()
    assert profile_data["success"] is True
    # The profile should have Nguyen Van A from user registration or parsed details
    assert profile_data["data"]["full_name"] in ("Nguyen Van A", "Nguyễn Văn A")

    # 7. Update Candidate Profile Section (e.g. Work Experience)
    work_payload = {
        "section": "work_experience",
        "data": {
            "work_experience": [
                {
                    "title": "Software Engineer",
                    "company": "FPT Software",
                    "location": "Ha Noi",
                    "start_date": "2024-01-01",
                    "end_date": "2025-01-01",
                    "is_current": False,
                    "description": "Developed React and FastAPI websites.",
                    "key_achievements": ["Best Intern"],
                    "technologies_used": ["React", "FastAPI"]
                }
            ]
        }
    }
    update_resp = await client.put("/api/v1/profile", json=work_payload, headers=headers)
    assert update_resp.status_code == 200
    updated_data = update_resp.json()
    assert updated_data["success"] is True
    assert len(updated_data["data"]["work_experience"]) == 1
    assert updated_data["data"]["work_experience"][0]["title"] == "Software Engineer"
    
    # Recalculated completeness score should be higher now
    assert updated_data["data"]["completeness_score"] > 0

    # 8. Check completeness endpoint breakdown
    comp_resp = await client.get("/api/v1/profile/completeness", headers=headers)
    assert comp_resp.status_code == 200
    comp_data = comp_resp.json()
    assert comp_data["success"] is True
    assert "overall_score" in comp_data["data"]
    assert "section_scores" in comp_data["data"]
    assert "suggestions" in comp_data["data"]

    # 9. Request profile export
    export_payload = {
        "format": "json"
    }
    export_resp = await client.post("/api/v1/profile/export", json=export_payload, headers=headers)
    assert export_resp.status_code == 200
    export_data = export_resp.json()
    assert export_data["success"] is True
    assert "download_url" in export_data["data"]
    assert export_data["data"]["download_url"].endswith(".json")
