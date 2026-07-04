import hashlib
import pytest
from sqlalchemy import select, delete
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job

pytestmark = pytest.mark.asyncio

PDF_BYTES = b"%PDF-1.4 fake jd content"
EXTERNAL_ID = f"upload-{hashlib.sha256(PDF_BYTES).hexdigest()[:16]}"


async def test_upload_jd_creates_searchable_job(
    client: AsyncClient, db_session: AsyncSession, monkeypatch
):
    # Mock text extraction (>50 chars so the text path is taken)
    monkeypatch.setattr(
        "app.services.impl.job_discovery_service_impl.TextExtractor.extract_text",
        lambda file_bytes, file_type: (
            "Senior Python Backend Engineer at FPT Software. Build APIs with "
            "FastAPI and PostgreSQL. Requires Python, Docker, Kubernetes."
        ),
    )

    # Mock the AI JD parser (avoid real API / quota)
    async def mock_parse_jd(self, text, pdf_bytes=None):
        return {
            "title": "Senior Python Backend Engineer",
            "company_name": "FPT Software",
            "location": "Ha Noi, Vietnam",
            "employment_type": "fulltime",
            "experience_level": "senior",
            "salary_min": 1500,
            "salary_max": 3000,
            "salary_currency": "USD",
            "description": "Build backend services.",
            "requirements": "5+ years Python.",
            "benefits": "Competitive salary.",
            "skills_required": ["Python", "FastAPI", "Docker", "Kubernetes"],
            "industry": "Software",
        }

    monkeypatch.setattr(
        "app.services.impl.gemini_provider.GeminiProvider.parse_job_description",
        mock_parse_jd,
    )

    # Register a user
    reg = await client.post("/api/v1/auth/register", json={
        "email": "jd@example.com", "password": "Password123!",
        "full_name": "JD Uploader", "terms_accepted": True,
    })
    assert reg.status_code == 201
    headers = {"Authorization": f"Bearer {reg.json()['data']['access_token']}"}

    try:
        # Upload the JD file
        files = {"file": ("jd.pdf", PDF_BYTES, "application/pdf")}
        resp = await client.post("/api/v1/jobs/upload", files=files, headers=headers)
        assert resp.status_code == 201, resp.text
        data = resp.json()["data"]
        assert data["title"] == "Senior Python Backend Engineer"
        assert data["company"] == "FPT Software"
        assert "Python" in data["skills_required"]

        # The job is persisted and becomes searchable via the jobs table
        job = (await db_session.execute(
            select(Job).where(Job.external_job_id == EXTERNAL_ID)
        )).scalar_one()
        assert job.source_platform == "upload"
        assert job.expires_at is None  # uploaded JDs never expire
        assert job.is_active is True
    finally:
        await db_session.execute(delete(Job).where(Job.external_job_id == EXTERNAL_ID))
        await db_session.commit()
