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

    async def search_jobs(self, query: str, page: int = 1) -> List[Dict[str, Any]]:
        if not self.api_key:
            logger.warning("JSEARCH_API_KEY not configured. Returning Mock job search results.")
            return self._mock_jobs()

        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "jsearch.p.rapidapi.com"
        }
        params = {
            "query": query,
            "page": str(page),
            "num_pages": "1"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.url,
                    headers=headers,
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                res_data = response.json()
                return res_data.get("data", [])
            except Exception as e:
                logger.error(f"JSearch API search_jobs error: {e}. Falling back to mock results.")
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
