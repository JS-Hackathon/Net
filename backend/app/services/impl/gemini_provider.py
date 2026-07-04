import base64
import json
import asyncio
import logging
from typing import Dict, Any
import httpx
from app.core.config import settings
from app.core.api_key_rotator import ApiKeyRotator
from app.services.interfaces.ai_provider import AIProvider
from app.services.prompts.matching_prompts import build_matching_prompt, JOB_MATCHING_PROMPT_VERSION
from app.services.prompts.resume_prompts import (
    RESUME_SCHEMA,
    build_resume_text_prompt,
    build_resume_pdf_prompt,
)

logger = logging.getLogger(__name__)


def _build_rotator() -> ApiKeyRotator | None:
    """Create a rotator from all configured Gemini keys, or None if no keys."""
    keys = settings.gemini_api_keys_list
    if not keys:
        return None
    return ApiKeyRotator(keys, cooldown_seconds=float(settings.GEMINI_KEY_COOLDOWN))


class GeminiProvider(AIProvider):
    def __init__(self):
        self.model = settings.GEMINI_MODEL              # matching
        self.parse_model = settings.GEMINI_PARSE_MODEL  # CV parsing (lighter, separate quota)
        self._base = "https://generativelanguage.googleapis.com/v1beta/models"
        self._rotator = _build_rotator()

        if self._rotator:
            logger.info(
                "GeminiProvider: key rotation enabled with %d key(s), cooldown=%ds",
                self._rotator.total_keys, settings.GEMINI_KEY_COOLDOWN,
            )
        else:
            logger.warning("GeminiProvider: no API keys configured — AI calls will fail.")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_api_key(self) -> str:
        """Get the next available API key from the rotator."""
        if not self._rotator:
            raise ValueError("GEMINI_API_KEY is not configured in environment variables.")
        return self._rotator.next_key()

    def _endpoint(self, model: str) -> str:
        return f"{self._base}/{model}:generateContent"

    def _headers(self, api_key: str) -> Dict[str, str]:
        # Send the key in a header, never in the URL query string, so it can't
        # leak into httpx error messages, logs, or stored error_message fields.
        return {"Content-Type": "application/json", "x-goog-api-key": api_key}

    @staticmethod
    def _retry_after_seconds(response: httpx.Response, default: float) -> float:
        ra = response.headers.get("Retry-After")
        if ra:
            try:
                return float(ra)
            except ValueError:
                pass
        return default

    # ------------------------------------------------------------------
    # Key rotation status (for health-check endpoint)
    # ------------------------------------------------------------------

    def rotator_status(self) -> dict:
        """Return rotation statistics for monitoring / debugging."""
        if not self._rotator:
            return {"enabled": False, "keys": []}
        return {
            "enabled": True,
            "total_keys": self._rotator.total_keys,
            "available_keys": self._rotator.available_count(),
            "keys": self._rotator.status(),
        }

    # ------------------------------------------------------------------
    # Resume parsing
    # ------------------------------------------------------------------

    async def parse_resume(self, text: str, pdf_bytes: bytes | None = None) -> Dict[str, Any]:
        """Parse a resume into the canonical structured schema.

        Two input modes:
          - text: extracted plain text (normal path).
          - pdf_bytes: the raw PDF, sent to Gemini directly for multimodal OCR
            (used when text extraction is empty, e.g. a scanned/image CV).

        Uses structured output (responseSchema) so the result always matches the
        CandidateProfile shape, and retries transient failures.
        Key rotation: on each attempt a fresh key is drawn; 429'd keys are put
        on cooldown and skipped on subsequent attempts.
        """
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

        max_attempts = max(3, self._rotator.total_keys if self._rotator else 3)
        last_status: int | None = None

        for attempt in range(max_attempts):
            api_key = self._get_api_key()
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        self._endpoint(self.parse_model),
                        json=payload,
                        headers=self._headers(api_key),
                        timeout=45.0,  # PDF/multimodal is heavier than text
                    )
                # Rate limit: mark this key and immediately try the next one
                if response.status_code == 429:
                    last_status = 429
                    wait = self._retry_after_seconds(response, default=60.0)
                    if self._rotator:
                        self._rotator.mark_rate_limited(api_key, extra_seconds=wait)
                    logger.warning(
                        "Gemini parse_resume 429 on key …%s; rotated to next (%d/%d)",
                        api_key[-4:], attempt + 1, max_attempts,
                    )
                    # Short delay only if we've exhausted all keys
                    if self._rotator and self._rotator.available_count() == 0:
                        await asyncio.sleep(min(wait, 5.0))
                    continue

                response.raise_for_status()
                res_data = response.json()
                content = res_data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(self._strip_json_fences(content))

            except httpx.HTTPStatusError as e:  # non-429 HTTP error
                last_status = e.response.status_code
                logger.warning(
                    "Gemini parse_resume attempt %d/%d: HTTP %d (key …%s)",
                    attempt + 1, max_attempts, last_status, api_key[-4:],
                )
                if attempt < max_attempts - 1:
                    await asyncio.sleep(0.5 * (attempt + 1))
            except Exception as e:  # noqa: BLE001 - network / JSON / shape errors
                # Log the type only — never the exception str (may embed the URL/key).
                logger.warning(
                    "Gemini parse_resume attempt %d/%d failed: %s (key …%s)",
                    attempt + 1, max_attempts, type(e).__name__, api_key[-4:],
                )
                if attempt < max_attempts - 1:
                    await asyncio.sleep(0.5 * (attempt + 1))

        if last_status == 429:
            raise ValueError(
                "Hệ thống AI đang quá tải (tất cả API key đều bị giới hạn). "
                "Vui lòng thử lại sau ít phút."
            )
        logger.error(
            "Gemini parse_resume failed after %d attempts (last HTTP status=%s).",
            max_attempts, last_status,
        )
        raise ValueError("Không phân tích được CV bằng AI. Vui lòng thử lại sau.")

    # ------------------------------------------------------------------
    # Job matching
    # ------------------------------------------------------------------

    async def match_job(self, profile: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        """Return a full structured job-candidate compatibility analysis.

        The prompt requests the detailed schema defined in matching_prompts. The
        request is retried with key rotation on failure.
        """
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

        max_attempts = max(2, self._rotator.total_keys if self._rotator else 2)
        last_error: Exception | None = None

        for attempt in range(max_attempts):
            api_key = self._get_api_key()
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(
                        self._endpoint(self.model),
                        json=payload,
                        headers=self._headers(api_key),
                        timeout=20.0
                    )
                    # Rate limit: rotate key and try next
                    if response.status_code == 429:
                        wait = self._retry_after_seconds(response, default=60.0)
                        if self._rotator:
                            self._rotator.mark_rate_limited(api_key, extra_seconds=wait)
                        logger.warning(
                            "Gemini match_job 429 on key …%s; rotated (%d/%d)",
                            api_key[-4:], attempt + 1, max_attempts,
                        )
                        if self._rotator and self._rotator.available_count() == 0:
                            await asyncio.sleep(min(wait, 5.0))
                        continue

                    response.raise_for_status()
                    res_data = response.json()
                    content = res_data["candidates"][0]["content"]["parts"][0]["text"]
                    return json.loads(content)
                except Exception as e:  # noqa: BLE001
                    last_error = e
                    logger.warning(
                        "Gemini match_job attempt %d/%d failed: %s (key …%s)",
                        attempt + 1, max_attempts, type(e).__name__, api_key[-4:],
                    )
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(1.0)

        logger.error("Gemini API match_job error after %d attempts: %s", max_attempts, last_error, exc_info=True)
        raise ValueError(f"Failed to match job with Gemini API: {str(last_error)}")

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

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
