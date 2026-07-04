import os
import json
import logging
from typing import List
from app.schemas.job_matching import RequirementMatch
from app.schemas.confidence import ConfidenceResult, ConfidenceSignals
from app.enums.match_status import MatchStatus
from app.services.interfaces.confidence_engine_service import IConfidenceEngineService

logger = logging.getLogger(__name__)

class ConfidenceEngineServiceImpl(IConfidenceEngineService):
    def __init__(self):
        self.static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "static")
        self.weights = self._load_json("confidence_weights.json")
        self.thresholds = self._load_json("confidence_thresholds.json")

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

    async def score(self, match_result: RequirementMatch) -> ConfidenceResult:
        # Default weights
        w_method = self.weights.get("matching_method", 0.35)
        w_strength = self.weights.get("evidence_strength", 0.25)
        w_freq = self.weights.get("evidence_frequency", 0.15)
        w_semantic = self.weights.get("semantic_similarity", 0.15)
        w_consistency = self.weights.get("context_consistency", 0.10)

        # 1. Matching Method Score
        method = match_result.matching_method
        if method == "canonical":
            method_score = 1.0
        elif method == "alias":
            method_score = 0.95
        elif method in ("ai", "cached"):
            method_score = 0.75
        else:
            method_score = 0.0

        # 2. Evidence Strength Score
        section_scores = {
            "skills": 1.0,
            "experience": 0.95,
            "projects": 0.90,
            "certifications": 0.90,
            "summary": 0.60
        }
        
        evidences = match_result.evidence
        if evidences:
            strength_score = max(section_scores.get(ev.section, 0.50) for ev in evidences)
        else:
            strength_score = 0.0

        # 3. Evidence Frequency Score
        freq = len(evidences)
        if freq >= 3:
            freq_score = 1.0
        elif freq == 2:
            freq_score = 0.90
        elif freq == 1:
            freq_score = 0.70
        else:
            freq_score = 0.0

        # 4. Semantic Similarity Score
        semantic_score = match_result.semantic_similarity

        # 5. Context Consistency Score
        sections = {ev.section for ev in evidences}
        if ("experience" in sections or "projects" in sections) and "skills" in sections:
            consistency_score = 1.0
        elif "experience" in sections or "projects" in sections:
            consistency_score = 0.85
        elif "skills" in sections:
            consistency_score = 0.70
        elif sections:
            consistency_score = 0.60
        else:
            consistency_score = 0.0

        # Composite Confidence Score
        confidence = (
            w_method * method_score +
            w_strength * strength_score +
            w_freq * freq_score +
            w_semantic * semantic_score +
            w_consistency * consistency_score
        )
        
        # Round confidence to 2 decimals
        confidence = round(min(max(confidence, 0.0), 1.0), 2)

        # Classification
        t_satisfied = self.thresholds.get("satisfied", 0.90)
        t_partial = self.thresholds.get("partial", 0.70)
        t_clarification = self.thresholds.get("clarification", 0.40)

        if confidence >= t_satisfied:
            status = MatchStatus.SATISFIED
        elif confidence >= t_partial:
            status = MatchStatus.PARTIAL
        elif confidence >= t_clarification:
            status = MatchStatus.CLARIFICATION
        else:
            status = MatchStatus.MISSING

        # Compile Reasoning
        reasoning = []
        if method == "canonical":
            reasoning.append("Exact canonical match found.")
        elif method == "alias":
            reasoning.append("Matched via alias dictionary.")
        elif method == "ai":
            reasoning.append("Classified semantically using AI.")
        elif method == "cached":
            reasoning.append("Retrieved mapping from AI cache.")
        else:
            reasoning.append("No technical mapping match.")

        if freq > 0:
            reasoning.append(f"Evidence found in {freq} section(s): {', '.join(sections)}.")
        else:
            reasoning.append("No active evidence found in the CV.")

        if semantic_score > 0.70:
            reasoning.append(f"High semantic similarity of {semantic_score:.2f} is detected.")

        if consistency_score >= 0.90:
            reasoning.append("Consistent references found across multiple sections.")

        return ConfidenceResult(
            requirement=match_result.requirement,
            matched_skill=match_result.matched_skill,
            matching_method=method,
            confidence=confidence,
            evidence_score=round(strength_score, 2),
            semantic_score=round(semantic_score, 2),
            status=status,
            signals=ConfidenceSignals(
                matching_method_score=round(method_score, 2),
                evidence_strength_score=round(strength_score, 2),
                evidence_frequency_score=round(freq_score, 2),
                semantic_similarity_score=round(semantic_score, 2),
                context_consistency_score=round(consistency_score, 2)
            ),
            evidence=[ev.model_dump() for ev in evidences],
            reasoning=reasoning
        )

    async def score_batch(self, match_results: List[RequirementMatch]) -> List[ConfidenceResult]:
        return [await self.score(mr) for mr in match_results]
