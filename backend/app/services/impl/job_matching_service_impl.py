import os
import json
import logging
import re
from typing import List
import httpx

from app.core.config import settings
from app.enums.requirement_priority import RequirementPriority
from app.enums.match_status import MatchStatus
from app.schemas.job_matching import (
    CandidateProfileInput,
    JobRequirement,
    RequirementMatchResult,
    PriorityInfo,
    MatchEvidence,
    RequirementMatch
)
from app.services.interfaces.job_matching_service import IJobMatchingService
from app.services.interfaces.skill_normalizer_service import ISkillNormalizerService
from app.services.interfaces.confidence_engine_service import IConfidenceEngineService

logger = logging.getLogger(__name__)

class JobMatchingServiceImpl(IJobMatchingService):
    def __init__(
        self,
        skill_normalizer: ISkillNormalizerService,
        confidence_engine: IConfidenceEngineService
    ):
        self.skill_normalizer = skill_normalizer
        self.confidence_engine = confidence_engine
        
        self.static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "static")
        self.prompts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "job_matching", "prompts")
        
        self.priority_scores = self._load_json("priority_scores.json")
        self.prompt_template = self._load_prompt("requirement_eval_v1.txt")

    def _load_json(self, filename: str) -> dict:
        filepath = os.path.join(self.static_dir, filename)
        try:
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            logger.warning(f"Static config file not found: {filepath}, using defaults.")
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

    def _collect_evidence(self, profile: CandidateProfileInput, keyword: str) -> List[MatchEvidence]:
        evidence = []
        kw_pattern = re.compile(rf"\b{re.escape(keyword.lower())}\b", re.IGNORECASE)

        # Check skills section
        for s in profile.skills:
            if kw_pattern.search(s.canonical) or kw_pattern.search(s.category):
                evidence.append(MatchEvidence(section="skills", text=f"Declared skill: {s.canonical} in category {s.category}"))

        # Check experience description
        for exp in profile.experience:
            if kw_pattern.search(exp.description) or kw_pattern.search(exp.title):
                evidence.append(MatchEvidence(section="experience", text=f"Role '{exp.title}' at {exp.company}: ... {exp.description[:100]} ..."))

        # Check project description
        for proj in profile.projects:
            if kw_pattern.search(proj.description) or kw_pattern.search(proj.name) or any(kw_pattern.search(tech) for tech in proj.technologies):
                evidence.append(MatchEvidence(section="projects", text=f"Project '{proj.name}': ... {proj.description[:100]} ..."))

        # Check certifications
        for cert in profile.certifications:
            if kw_pattern.search(cert):
                evidence.append(MatchEvidence(section="certifications", text=f"Certificate: {cert}"))

        # Check summary
        if profile.summary and kw_pattern.search(profile.summary):
            evidence.append(MatchEvidence(section="summary", text=f"Summary note: {profile.summary[:120]}"))

        return evidence[:3]  # Limit to top 3 evidence pieces for layout neatness

    async def evaluate(
        self,
        candidate_profile: CandidateProfileInput,
        requirement: JobRequirement,
    ) -> RequirementMatchResult:
        p_level = requirement.priority
        p_score = self.priority_scores.get(p_level.value, 0.50)
        priority_info = PriorityInfo(level=p_level, score=p_score)

        # Helper to construct missing output
        def missing_result(reason: str) -> RequirementMatchResult:
            return RequirementMatchResult(
                requirement_id=requirement.id,
                requirement=requirement.canonical,
                status=MatchStatus.MISSING,
                priority=priority_info,
                confidence=0.0,
                evidence_score=0.0,
                matched_skill="None",
                matching_method="none",
                evidence=[],
                reasoning=[reason],
                contribution=0.0
            )

        # Stage 1: Exact Canonical Match
        exact_match = None
        for s in candidate_profile.skills:
            if s.canonical.lower() == requirement.canonical.lower():
                exact_match = s
                break

        if exact_match:
            evidence = self._collect_evidence(candidate_profile, exact_match.canonical)
            req_match = RequirementMatch(
                requirement=requirement.canonical,
                matched_skill=exact_match.canonical,
                matching_method="canonical",
                semantic_similarity=1.0,
                evidence=evidence
            )
            conf_res = await self.confidence_engine.score(req_match)
            return RequirementMatchResult(
                requirement_id=requirement.id,
                requirement=requirement.canonical,
                status=conf_res.status,
                priority=priority_info,
                confidence=conf_res.confidence,
                evidence_score=conf_res.evidence_score,
                matched_skill=exact_match.canonical,
                matching_method="canonical",
                evidence=[MatchEvidence(section=ev["section"], text=ev["text"]) for ev in conf_res.evidence],
                reasoning=conf_res.reasoning,
                contribution=round(priority_info.score * conf_res.confidence, 2)
            )

        # Stage 2: Related Skill Match (Category Match)
        category_match = None
        for s in candidate_profile.skills:
            if s.category.lower() == requirement.category.lower():
                # Prefer matches with higher confidence or matching method
                if not category_match or s.confidence > category_match.confidence:
                    category_match = s

        if category_match:
            evidence = self._collect_evidence(candidate_profile, category_match.canonical)
            req_match = RequirementMatch(
                requirement=requirement.canonical,
                matched_skill=category_match.canonical,
                matching_method="alias",
                semantic_similarity=0.85,
                evidence=evidence
            )
            conf_res = await self.confidence_engine.score(req_match)
            return RequirementMatchResult(
                requirement_id=requirement.id,
                requirement=requirement.canonical,
                status=conf_res.status,
                priority=priority_info,
                confidence=conf_res.confidence,
                evidence_score=conf_res.evidence_score,
                matched_skill=category_match.canonical,
                matching_method="alias",
                evidence=[MatchEvidence(section=ev["section"], text=ev["text"]) for ev in conf_res.evidence],
                reasoning=conf_res.reasoning,
                contribution=round(priority_info.score * conf_res.confidence, 2)
            )

        # Stage 3: AI Semantic Evaluation Fallback (Gemini)
        ai_match = await self._evaluate_ai_fallback(candidate_profile, requirement)
        if ai_match and ai_match.get("is_satisfied", False):
            evidence = self._collect_evidence(candidate_profile, requirement.canonical)
            # If no keyword evidence found, we use generic summary context as fallback evidence
            if not evidence and candidate_profile.summary:
                evidence.append(MatchEvidence(section="summary", text=candidate_profile.summary[:150]))
            
            similarity = ai_match.get("confidence_hint", 0.75)
            req_match = RequirementMatch(
                requirement=requirement.canonical,
                matched_skill=requirement.canonical,
                matching_method="ai",
                semantic_similarity=similarity,
                evidence=evidence
            )
            conf_res = await self.confidence_engine.score(req_match)
            return RequirementMatchResult(
                requirement_id=requirement.id,
                requirement=requirement.canonical,
                status=conf_res.status,
                priority=priority_info,
                confidence=conf_res.confidence,
                evidence_score=conf_res.evidence_score,
                matched_skill=requirement.canonical,
                matching_method="ai",
                evidence=[MatchEvidence(section=ev["section"], text=ev["text"]) for ev in conf_res.evidence],
                reasoning=[ai_match.get("reasoning", "Semantic match identified by AI.")] + conf_res.reasoning,
                contribution=round(priority_info.score * conf_res.confidence, 2)
            )

        return missing_result("No exact, related, or semantic skill match found in candidate profile.")

    async def _evaluate_ai_fallback(self, profile: CandidateProfileInput, requirement: JobRequirement) -> dict:
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            logger.warning("GEMINI_API_KEY is not configured, bypassing Stage 3 AI Match.")
            return {"is_satisfied": False, "confidence_hint": 0.0, "reasoning": "No API Key configured."}

        skills_list = [s.canonical for s in profile.skills]
        evidence_text = []
        for exp in profile.experience:
            evidence_text.append(f"{exp.title} at {exp.company}: {exp.description}")
        for proj in profile.projects:
            evidence_text.append(f"Project {proj.name}: {proj.description}")

        prompt = self.prompt_template.format(
            requirement_text=requirement.text,
            candidate_skills=json.dumps(skills_list),
            candidate_evidence=json.dumps(evidence_text[:5])
        )

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
                response = await client.post(url, json=payload, headers=headers, timeout=12.0)
                response.raise_for_status()
                res_data = response.json()
                content = res_data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(content)
            except Exception as e:
                logger.error(f"Failed to call Gemini requirement evaluator: {e}")
                return {"is_satisfied": False, "confidence_hint": 0.0, "reasoning": "Gemini API call failed."}

    async def evaluate_all(
        self,
        candidate_profile: CandidateProfileInput,
        requirements: List[JobRequirement],
    ) -> List[RequirementMatchResult]:
        results = []
        for req in requirements:
            results.append(await self.evaluate(candidate_profile, req))
        return results
