import logging
from typing import List, Dict, Any
import httpx
from app.core.config import settings
from app.services.interfaces.jsearch_service import JSearchService

logger = logging.getLogger(__name__)

class JSearchServiceImpl(JSearchService):
    def __init__(self):
        self.api_key = settings.JSEARCH_API_KEY
        self.url = "https://jsearch.p.rapidapi.com/search-v2"

    async def search_jobs(
        self,
        query: str,
        page: int = 1,
        *,
        country: str | None = None,
        date_posted: str | None = None,
        remote_only: bool = False,
        employment_types: str | None = None,
    ) -> List[Dict[str, Any]]:
        if not self.api_key:
            logger.warning("JSEARCH_API_KEY not configured. Returning Mock job search results.")
            return self._mock_jobs()

        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "jsearch.p.rapidapi.com"
        }
        # Filter server-side (previously these were configured but never sent).
        # Only send country when set — JSearch has sparse VN coverage, so an empty
        # country returns real (global) jobs instead of nothing.
        params = {
            "query": query,
            "page": str(page),
            "num_pages": "1",
        }
        # Force country to "vn" (Vietnam) to restrict searches only to Vietnam
        _country = "vn"
        params["country"] = _country
        _date = (date_posted or settings.JSEARCH_DATE_POSTED or "").strip()
        if _date and _date != "all":  # "all" is JSearch's default; omit it
            params["date_posted"] = _date
        if remote_only:
            params["work_from_home"] = "true"
        if employment_types:
            params["employment_types"] = employment_types

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.url,
                    headers=headers,
                    params=params,
                    timeout=15.0  # free-tier JSearch can be slow
                )
                response.raise_for_status()
                res_data = response.json()
                jobs = self._as_job_list(res_data.get("data"))
                if not jobs:
                    # Odd shape (throttle/error object) — log keys (not body) to debug.
                    logger.warning(
                        f"JSearch returned no usable jobs (top keys={list(res_data.keys())}); "
                        "falling back to mock/empty."
                    )
                return jobs
            except Exception as e:
                logger.error(f"JSearch API search_jobs error: {type(e).__name__}. Falling back to mock/empty.")
                return []

    @staticmethod
    def _as_job_list(data: Any) -> List[Dict[str, Any]]:
        """Normalize the JSearch `data` field to a list of job dicts.

        Robust to response-shape variance: `data` may be a list, a dict wrapping
        a list (jobs/results/data), or a single job object. Anything else -> [].
        """
        if isinstance(data, list):
            return [j for j in data if isinstance(j, dict)]
        if isinstance(data, dict):
            for key in ("jobs", "results", "data"):
                inner = data.get(key)
                if isinstance(inner, list):
                    return [j for j in inner if isinstance(j, dict)]
            if data.get("job_id") or data.get("job_title"):
                return [data]
        return []

    @staticmethod
    def _mock_jobs() -> List[Dict[str, Any]]:
        """Richer mock dataset (skills, remote flag, salary, posted date) so the
        Phase 3 discovery/matching demo works end-to-end without a JSearch key."""
        return [
            {
                "job_id": "mock-job-1",
                "job_title": "Senior React Frontend Developer",
                "employer_name": "WebTech Group",
                "employer_company_type": "Technology",
                "job_description": "Build dynamic user interfaces using React, TypeScript, Next.js and TailwindCSS. Collaborate with designers and backend engineers.",
                "job_city": "Ho Chi Minh City",
                "job_country": "Vietnam",
                "job_employment_type": "FULLTIME",
                "job_is_remote": True,
                "job_apply_link": "https://example.com/apply/1",
                "job_min_salary": 1800,
                "job_max_salary": 3000,
                "job_salary_currency": "USD",
                "job_publisher": "LinkedIn",
                "job_posted_at_datetime_utc": "2026-06-30T00:00:00Z",
                "job_required_skills": ["React", "TypeScript", "Next.js", "TailwindCSS", "Redux", "GraphQL"],
                "job_required_experience": {"required_experience_in_months": 60},
            },
            {
                "job_id": "mock-job-2",
                "job_title": "FastAPI Backend Developer",
                "employer_name": "AI Solutions Inc.",
                "employer_company_type": "Artificial Intelligence",
                "job_description": "Design and build REST APIs with FastAPI, PostgreSQL and SQLAlchemy. Deploy to AWS.",
                "job_city": "Ha Noi",
                "job_country": "Vietnam",
                "job_employment_type": "FULLTIME",
                "job_is_remote": False,
                "job_apply_link": "https://example.com/apply/2",
                "job_min_salary": 1500,
                "job_max_salary": 2500,
                "job_salary_currency": "USD",
                "job_publisher": "Indeed",
                "job_posted_at_datetime_utc": "2026-07-01T00:00:00Z",
                "job_required_skills": ["Python", "FastAPI", "PostgreSQL", "SQLAlchemy", "AWS", "Docker"],
                "job_required_experience": {"required_experience_in_months": 36},
            },
            {
                "job_id": "mock-job-3",
                "job_title": "Full-stack Engineer (React + Node)",
                "employer_name": "Startup Labs",
                "employer_company_type": "Startup",
                "job_description": "Own features end-to-end across a React frontend and a Node.js/Express backend with MongoDB.",
                "job_city": "Da Nang",
                "job_country": "Vietnam",
                "job_employment_type": "FULLTIME",
                "job_is_remote": True,
                "job_apply_link": "https://example.com/apply/3",
                "job_min_salary": 1200,
                "job_max_salary": 2200,
                "job_salary_currency": "USD",
                "job_publisher": "Glassdoor",
                "job_posted_at_datetime_utc": "2026-06-28T00:00:00Z",
                "job_required_skills": ["React", "TypeScript", "Node.js", "Express", "MongoDB", "Docker"],
                "job_required_experience": {"required_experience_in_months": 24},
            },
            {
                "job_id": "mock-job-4",
                "job_title": "Junior Frontend Developer",
                "employer_name": "Creative Digital",
                "employer_company_type": "Agency",
                "job_description": "Entry-level role building responsive websites with HTML, CSS, JavaScript and React.",
                "job_city": "Ho Chi Minh City",
                "job_country": "Vietnam",
                "job_employment_type": "FULLTIME",
                "job_is_remote": False,
                "job_apply_link": "https://example.com/apply/4",
                "job_min_salary": 700,
                "job_max_salary": 1200,
                "job_salary_currency": "USD",
                "job_publisher": "LinkedIn",
                "job_posted_at_datetime_utc": "2026-07-02T00:00:00Z",
                "job_required_skills": ["HTML", "CSS", "JavaScript", "React"],
                "job_required_experience": {"required_experience_in_months": 6},
            },
            {
                "job_id": "mock-job-5",
                "job_title": "DevOps Engineer",
                "employer_name": "CloudOps Vietnam",
                "employer_company_type": "Cloud Services",
                "job_description": "Manage CI/CD pipelines, Kubernetes clusters and infrastructure-as-code on AWS.",
                "job_city": "Remote",
                "job_country": "Vietnam",
                "job_employment_type": "FULLTIME",
                "job_is_remote": True,
                "job_apply_link": "https://example.com/apply/5",
                "job_min_salary": 2000,
                "job_max_salary": 3500,
                "job_salary_currency": "USD",
                "job_publisher": "Indeed",
                "job_posted_at_datetime_utc": "2026-06-25T00:00:00Z",
                "job_required_skills": ["AWS", "Kubernetes", "Docker", "Terraform", "CI/CD", "Linux"],
                "job_required_experience": {"required_experience_in_months": 48},
            },
        ]
