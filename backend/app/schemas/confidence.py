from pydantic import BaseModel, Field
from app.enums.match_status import MatchStatus

class ConfidenceSignals(BaseModel):
    matching_method_score: float = Field(..., ge=0.0, le=1.0)
    evidence_strength_score: float = Field(..., ge=0.0, le=1.0)
    evidence_frequency_score: float = Field(..., ge=0.0, le=1.0)
    semantic_similarity_score: float = Field(..., ge=0.0, le=1.0)
    context_consistency_score: float = Field(..., ge=0.0, le=1.0)

class ConfidenceResult(BaseModel):
    requirement: str = Field(..., description="Canonical skill that was evaluated.")
    matched_skill: str = Field(..., description="Canonical skill found in candidate profile.")
    matching_method: str = Field(..., description="Method used to produce the match.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Final composite confidence score.")
    evidence_score: float = Field(..., ge=0.0, le=1.0, description="Aggregated evidence strength score.")
    semantic_score: float = Field(..., ge=0.0, le=1.0, description="Semantic similarity score (0.0 if unavailable).")
    status: MatchStatus = Field(..., description="Requirement satisfaction status derived from confidence.")
    signals: ConfidenceSignals = Field(..., description="Breakdown of individual scoring signals.")
    evidence: list[dict] = Field(..., description="Evidence items that supported this result.")
    reasoning: list[str] = Field(..., description="Human-readable explanation for the confidence score.")
