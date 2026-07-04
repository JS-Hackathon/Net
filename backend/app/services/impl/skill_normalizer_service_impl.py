import os
import json
import logging
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from app.core.config import settings
from app.schemas.skill_normalizer import NormalizedSkill
from app.models.ai_skill_mapping import AISkillMapping
from app.services.interfaces.skill_normalizer_service import ISkillNormalizerService

logger = logging.getLogger(__name__)

class SkillNormalizerServiceImpl(ISkillNormalizerService):
    def __init__(self, db: AsyncSession):
        self.db = db
        self.static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "static")
        self.prompts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "skill_normalizer", "prompts")
        
        self.aliases = self._load_json("aliases.json")
        self.canonical_mappings = self._load_json("canonical_mappings.json")
        self.prompt_template = self._load_prompt("skill_classify_v1.txt")

    def _load_json(self, filename: str) -> dict:
        filepath = os.path.join(self.static_dir, filename)
        try:
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            logger.warning(f"Static config file not found: {filepath}, using empty dict.")
            return {}
        except Exception as e:
            logger.error(f"Error loading static config {filename}: {e}")
            return {}

    def _load_prompt(self, filename: str) -> str:
        filepath = os.path.join(self.prompts_dir, filename)
        try:
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    return f.read()
            logger.warning(f"Prompt file not found: {filepath}")
            return ""
        except Exception as e:
            logger.error(f"Error loading prompt {filename}: {e}")
            return ""

    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        # Lowercase, trim, and collapse duplicated spaces
        cleaned = text.lower().strip()
        # Remove common level indications in parentheses
        import re
        cleaned = re.sub(r"\s*\(.*?\)\s*", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned

    async def normalize(self, skill: str) -> NormalizedSkill:
        cleaned = self._clean_text(skill)
        if not cleaned:
            return NormalizedSkill(
                raw=skill,
                normalized="",
                canonical="Unknown",
                category="Unknown",
                confidence=0.0,
                mapping_method="dictionary"
            )

        # 1. Alias Resolution
        resolved_alias = self.aliases.get(cleaned, cleaned)

        # 2. Canonical Mapping (dictionary)
        if resolved_alias in self.canonical_mappings:
            canonical = self.canonical_mappings[resolved_alias]
            # Infer category (usually same as canonical or group name)
            category = canonical
            # If alias was used, return mapping_method="alias", else "dictionary"
            method = "alias" if resolved_alias != cleaned else "dictionary"
            return NormalizedSkill(
                raw=skill,
                normalized=cleaned,
                canonical=canonical,
                category=category,
                confidence=1.0,
                mapping_method=method
            )

        # 3. Check Database Cache
        stmt = select(AISkillMapping).where(AISkillMapping.raw_skill == skill)
        cached = (await self.db.execute(stmt)).scalar_one_or_none()
        if cached:
            return NormalizedSkill(
                raw=skill,
                normalized=cached.normalized,
                canonical=cached.canonical,
                category=cached.category,
                confidence=cached.confidence,
                mapping_method="cached"
            )

        # 4. AI Fallback (Gemini 2.5 Flash Lite)
        normalized_data = await self._call_gemini_fallback(skill)
        
        # Save to DB cache
        try:
            async with self.db.begin_nested():
                new_mapping = AISkillMapping(
                    raw_skill=skill,
                    normalized=cleaned,
                    canonical=normalized_data.get("canonical", "Unknown"),
                    category=normalized_data.get("category", "Unknown"),
                    confidence=normalized_data.get("confidence", 0.5)
                )
                self.db.add(new_mapping)
                await self.db.commit()
        except Exception as cache_err:
            logger.warning(f"Failed to cache skill normalizer output in DB: {cache_err}")

        return NormalizedSkill(
            raw=skill,
            normalized=cleaned,
            canonical=normalized_data.get("canonical", "Unknown"),
            category=normalized_data.get("category", "Unknown"),
            confidence=normalized_data.get("confidence", 0.5),
            mapping_method="ai"
        )

    async def _call_gemini_fallback(self, skill: str) -> dict:
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            logger.warning("GEMINI_API_KEY is not configured, returning fallback mock values.")
            return {"canonical": skill.title(), "category": "General", "confidence": 0.5}

        prompt = self.prompt_template.format(raw_skill=skill)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json"
            }
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=headers, timeout=10.0)
                response.raise_for_status()
                res_data = response.json()
                content = res_data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(content)
            except Exception as e:
                logger.error(f"Failed to call Gemini normalizer fallback: {e}")
                return {"canonical": skill.title(), "category": "General", "confidence": 0.5}

    async def normalize_batch(self, skills: List[str]) -> List[NormalizedSkill]:
        results = []
        for s in skills:
            results.append(await self.normalize(s))
        return results
