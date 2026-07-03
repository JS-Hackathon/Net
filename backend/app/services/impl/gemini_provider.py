import json
import asyncio
import logging
from typing import Dict, Any
import httpx
from app.core.config import settings
from app.services.interfaces.ai_provider import AIProvider
from app.services.prompts.matching_prompts import build_matching_prompt, JOB_MATCHING_PROMPT_VERSION

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

    @property
    def model_version(self) -> str:
        return f"{self.model}"

    @property
    def matching_prompt_version(self) -> str:
        return JOB_MATCHING_PROMPT_VERSION

    async def match_job(self, profile: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        """Return a full structured job-candidate compatibility analysis.

        The prompt requests the detailed schema defined in matching_prompts. The
        request is retried once on failure (per NFR: retry AI failures).
        """
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured in environment variables.")

        headers = {"Content-Type": "application/json"}
        prompt = build_matching_prompt(profile, job)
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                # Low temperature for consistent, deterministic analysis.
                "temperature": 0.2,
                "topP": 0.8,
                "maxOutputTokens": 2048,
                "responseMimeType": "application/json"
            }
        }

        last_error: Exception | None = None
        for attempt in range(2):  # initial try + 1 retry
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(
                        f"{self.url}?key={self.api_key}",
                        json=payload,
                        headers=headers,
                        timeout=20.0
                    )
                    response.raise_for_status()
                    res_data = response.json()
                    content = res_data["candidates"][0]["content"]["parts"][0]["text"]
                    return json.loads(content)
                except Exception as e:  # noqa: BLE001
                    last_error = e
                    logger.warning(f"Gemini match_job attempt {attempt + 1} failed: {e}")
                    if attempt == 0:
                        await asyncio.sleep(1.0)

        logger.error(f"Gemini API match_job error after retries: {last_error}", exc_info=True)
        raise ValueError(f"Failed to match job with Gemini API: {str(last_error)}")
