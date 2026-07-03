import json
import logging
from typing import Dict, Any
import httpx
from app.core.config import settings
from app.services.interfaces.ai_provider import AIProvider

logger = logging.getLogger(__name__)

class GeminiProvider(AIProvider):
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = "gemini-2.5-flash"
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    async def parse_resume(self, text: str) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured in environment variables.")

        headers = {"Content-Type": "application/json"}
        prompt = (
            "You are an expert resume parser. Parse the following resume text into a structured JSON format. "
            "Return only the raw JSON. The JSON schema must strictly contain keys: "
            "'skills' (array of strings), 'education' (array of objects with 'degree', 'institution', 'graduation_year'), "
            "'experience' (array of objects with 'title', 'company', 'duration', 'responsibilities'), "
            "'projects' (array of objects with 'name', 'description'), and 'certifications' (array of strings). "
            f"\n\nResume Text:\n{text}"
        )
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "responseMimeType": "application/json"
            }
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.url}?key={self.api_key}",
                    json=payload,
                    headers=headers,
                    timeout=15.0
                )
                response.raise_for_status()
                res_data = response.json()
                content = res_data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(content)
            except Exception as e:
                logger.error(f"Gemini API parse_resume error: {e}", exc_info=True)
                raise ValueError(f"Failed to parse resume with Gemini API: {str(e)}")

    async def match_job(self, profile: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured in environment variables.")

        headers = {"Content-Type": "application/json"}
        prompt = (
            "Compare the candidate profile with the job description. "
            "Return a structured JSON with keys: 'match_score' (integer between 0 and 100), "
            "'strengths' (array of strings), 'weaknesses' (array of strings), and "
            "'skill_gaps' (array of objects with 'skill', 'priority', 'suggestion'). "
            "Return only the raw JSON.\n\n"
            f"Candidate Profile:\n{json.dumps(profile)}\n\n"
            f"Job Description:\n{json.dumps(job)}"
        )
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "responseMimeType": "application/json"
            }
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.url}?key={self.api_key}",
                    json=payload,
                    headers=headers,
                    timeout=15.0
                )
                response.raise_for_status()
                res_data = response.json()
                content = res_data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(content)
            except Exception as e:
                logger.error(f"Gemini API match_job error: {e}", exc_info=True)
                raise ValueError(f"Failed to match job with Gemini API: {str(e)}")
