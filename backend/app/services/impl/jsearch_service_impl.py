import logging
from typing import List, Dict, Any
import httpx
from app.core.config import settings
from app.services.interfaces.jsearch_service import JSearchService

logger = logging.getLogger(__name__)

class JSearchServiceImpl(JSearchService):
    def __init__(self):
        self.api_key = settings.JSEARCH_API_KEY
        self.url = "https://jsearch.p.rapidapi.com/search"

    async def search_jobs(self, query: str, page: int = 1) -> List[Dict[str, Any]]:
        if not self.api_key:
            logger.warning("JSEARCH_API_KEY not configured. Returning Mock job search results.")
            return [
                {
                    "job_id": "mock-job-1",
                    "job_title": "FastAPI Backend Developer",
                    "employer_name": "AI Solutions Inc.",
                    "job_description": "We are looking for a Python developer with experience in FastAPI, PostgreSQL, and AWS.",
                    "job_city": "Ho Chi Minh City",
                    "job_country": "Vietnam",
                    "job_apply_link": "https://example.com/apply/1",
                    "job_max_salary": 2500,
                    "job_salary_currency": "USD"
                },
                {
                    "job_id": "mock-job-2",
                    "job_title": "React Frontend Developer",
                    "employer_name": "WebTech Group",
                    "job_description": "Join our team to build dynamic user interfaces using React 19, TypeScript, and Next.js.",
                    "job_city": "Hanoi",
                    "job_country": "Vietnam",
                    "job_apply_link": "https://example.com/apply/2",
                    "job_max_salary": 2000,
                    "job_salary_currency": "USD"
                }
            ]

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
