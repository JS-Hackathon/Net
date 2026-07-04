from typing import Protocol
from app.schemas.job_matching import CandidateProfileInput, JobRequirement, RequirementMatchResult

class IJobMatchingService(Protocol):
    async def evaluate(
        self,
        candidate_profile: CandidateProfileInput,
        requirement: JobRequirement,
    ) -> RequirementMatchResult:
        """Evaluate a single job requirement against the candidate profile.

        Args:
            candidate_profile (CandidateProfileInput): Structured candidate profile
                from ResumeAnalysisService with normalized skills and CV sections.
            requirement (JobRequirement): A single normalized JD requirement with
                canonical form and priority section.

        Returns:
            RequirementMatchResult: Atomic evaluation result including status,
                confidence, evidence, reasoning, and weighted contribution.
        """
        ...

    async def evaluate_all(
        self,
        candidate_profile: CandidateProfileInput,
        requirements: list[JobRequirement],
    ) -> list[RequirementMatchResult]:
        """Evaluate all job requirements against the candidate profile.

        Args:
            candidate_profile (CandidateProfileInput): Candidate profile.
            requirements (list[JobRequirement]): Full list of JD requirements.

        Returns:
            list[RequirementMatchResult]: One result per requirement, in same order.
                Aggregated as the Requirement Matrix for downstream services.
        """
        ...
