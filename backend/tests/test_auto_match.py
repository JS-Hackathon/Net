import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, delete
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.candidate_profile import CandidateProfile
from app.models.job import Job

pytestmark = pytest.mark.asyncio


async def test_auto_match_returns_companies_and_scenario(
    client: AsyncClient, db_session: AsyncSession, monkeypatch
):
    # Mock the AI interview scenario so the test never hits the real API/quota.
    async def mock_scenario(self, profile, job):
        return {
            "opening": "Xin chào",
            "focus_skills": ["Python"],
            "gaps_to_prepare": ["Kubernetes"],
            "questions": [
                {"category": "technical", "question": "Bạn dùng FastAPI thế nào?",
                 "assesses": "Chiều sâu kỹ thuật", "answer_tip": "Nêu ví dụ dự án."}
            ],
            "preparation_tips": ["Ôn lại Python"],
            "closing": "Chúc may mắn",
        }

    monkeypatch.setattr(
        "app.services.impl.gemini_provider.GeminiProvider.generate_interview_scenario",
        mock_scenario,
    )

    # 1. Register a candidate
    reg = await client.post("/api/v1/auth/register", json={
        "email": "automatch@example.com",
        "password": "Password123!",
        "full_name": "Auto Match",
        "terms_accepted": True,
    })
    assert reg.status_code == 201
    token = reg.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    user = (await db_session.execute(
        select(User).where(User.email == "automatch@example.com")
    )).scalar_one()

    # 2. Give the (auto-created) profile skills + seed a matching job
    profile = (await db_session.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == user.id)
    )).scalar_one_or_none()
    if profile is None:
        profile = CandidateProfile(
            user_id=user.id, completeness_score=0.0, profile_strength="basic",
            is_public=False, is_searchable=True,
            work_experience=[], education=[], soft_skills=[],
            certifications=[], languages=[], projects=[], achievements=[],
        )
        db_session.add(profile)
    profile.technical_skills = [{"name": "Python"}, {"name": "FastAPI"}]
    now = datetime.now(timezone.utc)
    db_session.add(Job(
        external_job_id="autotest-job-1",
        title="Python Backend Engineer",
        company_name="FPT Software",
        salary_currency="USD",
        skills_required=["Python", "Docker"],
        is_active=True,
        cached_at=now,
        expires_at=now + timedelta(hours=4),
    ))
    await db_session.commit()

    try:
        # 3. One-shot Auto Match
        resp = await client.post("/api/v1/matches/auto", headers=headers)
        assert resp.status_code == 201, resp.text
        data = resp.json()["data"]

        # Companies ranked deterministically (no AI) — must be non-empty
        assert len(data["companies"]) >= 1
        assert "match_score" in data["companies"][0]

        # Interview scenario for the top company
        assert data["target"]["job_id"]
        assert len(data["interview_scenario"]["questions"]) >= 1
        assert data["interview_scenario"]["questions"][0]["question"]
    finally:
        # Clean up the seeded job (cleanup_db fixture does not manage jobs)
        await db_session.execute(delete(Job).where(Job.external_job_id == "autotest-job-1"))
        await db_session.commit()
