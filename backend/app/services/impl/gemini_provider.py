import base64
import json
import asyncio
import logging
from typing import Dict, Any
import httpx
from app.core.config import settings
from app.services.interfaces.ai_provider import AIProvider
from app.services.prompts.matching_prompts import build_matching_prompt, JOB_MATCHING_PROMPT_VERSION
from app.services.prompts.resume_prompts import (
    RESUME_SCHEMA,
    build_resume_text_prompt,
    build_resume_pdf_prompt,
)

logger = logging.getLogger(__name__)

class GeminiProvider(AIProvider):
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = "gemini-2.5-flash"
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    async def parse_resume(self, text: str, pdf_bytes: bytes | None = None) -> Dict[str, Any]:
        """Parse a resume into the canonical structured schema.

        Two input modes:
          - text: extracted plain text (normal path).
          - pdf_bytes: the raw PDF, sent to Gemini directly for multimodal OCR
            (used when text extraction is empty, e.g. a scanned/image CV).

        Uses structured output (responseSchema) so the result always matches the
        CandidateProfile shape, and retries transient failures.
        """
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured in environment variables.")

        headers = {"Content-Type": "application/json"}

        if pdf_bytes is not None:
            parts = [
                {"text": build_resume_pdf_prompt()},
                {"inline_data": {
                    "mime_type": "application/pdf",
                    "data": base64.b64encode(pdf_bytes).decode("ascii"),
                }},
            ]
        else:
            parts = [{"text": build_resume_text_prompt(text)}]

        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 8192,
                "responseMimeType": "application/json",
                "responseSchema": RESUME_SCHEMA,
            },
        }

        last_error: Exception | None = None
        for attempt in range(3):  # initial try + 2 retries
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.url}?key={self.api_key}",
                        json=payload,
                        headers=headers,
                        timeout=45.0,  # PDF/multimodal is heavier than text
                    )
                    response.raise_for_status()
                    res_data = response.json()
                    content = res_data["candidates"][0]["content"]["parts"][0]["text"]
                    return json.loads(self._strip_json_fences(content))
            except Exception as e:  # noqa: BLE001 - normalize any client/parse error
                last_error = e
                logger.warning(f"Gemini parse_resume attempt {attempt + 1}/3 failed: {e}")
                if attempt < 2:
                    await asyncio.sleep(0.5 * (attempt + 1))

        logger.error(f"Gemini API parse_resume error after retries: {last_error}", exc_info=True)
        raise ValueError(f"Failed to parse resume with Gemini API: {last_error}")

    @staticmethod
    def _strip_json_fences(content: str) -> str:
        """Defensively remove ```json ... ``` fences if the model wraps the JSON."""
        s = content.strip()
        if s.startswith("```"):
            first_nl = s.find("\n")
            if first_nl != -1:
                s = s[first_nl + 1:]
            if s.rstrip().endswith("```"):
                s = s.rstrip()[:-3]
        return s.strip()

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
