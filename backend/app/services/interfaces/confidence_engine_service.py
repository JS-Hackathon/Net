from typing import Protocol
from app.schemas.job_matching import RequirementMatch
from app.schemas.confidence import ConfidenceResult

class IConfidenceEngineService(Protocol):
    async def score(self, match_result: RequirementMatch) -> ConfidenceResult:
        """Calculate a deterministic confidence score for a single requirement match.

        Args:
            match_result (RequirementMatch): Output from JobMatchingService containing
                matched skill, matching method, semantic similarity, and evidence.

        Returns:
            ConfidenceResult: Composite confidence score, status classification,
                per-signal breakdown, evidence, and human-readable reasoning.
        """
        ...

    async def score_batch(self, match_results: list[RequirementMatch]) -> list[ConfidenceResult]:
        """Calculate confidence scores for a list of requirement matches.

        Args:
            match_results (list[RequirementMatch]): List of match results from JobMatchingService.

        Returns:
            list[ConfidenceResult]: Confidence results in same order as input.
        """
        ...
