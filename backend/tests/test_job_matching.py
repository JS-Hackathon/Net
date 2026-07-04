import pytest
from app.services.impl.skill_normalizer_service_impl import SkillNormalizerServiceImpl
from app.services.impl.confidence_engine_service_impl import ConfidenceEngineServiceImpl
from app.services.impl.job_matching_service_impl import JobMatchingServiceImpl
from app.schemas.job_matching import CandidateProfileInput, ProfileSkill, JobRequirement
from app.enums.requirement_priority import RequirementPriority
from app.enums.match_status import MatchStatus

@pytest.mark.asyncio
async def test_job_matching_pipeline(db_session):
    normalizer = SkillNormalizerServiceImpl(db=db_session)
    confidence = ConfidenceEngineServiceImpl()
    matcher = JobMatchingServiceImpl(normalizer, confidence)

    # Prepare Candidate Profile
    profile = CandidateProfileInput(
        user_id="user-123",
        skills=[
            ProfileSkill(canonical="Containerization", category="DevOps", confidence=1.0, mapping_method="dictionary"),
            ProfileSkill(canonical="Backend Development", category="Backend Development", confidence=1.0, mapping_method="dictionary")
        ],
        experience=[],
        projects=[],
        certifications=[]
    )

    # Prepare Job Requirement
    requirement = JobRequirement(
        id="REQ1",
        text="Docker expertise is preferred",
        canonical="Containerization",
        category="DevOps",
        section="must_have",
        priority=RequirementPriority.CRITICAL
    )

    res = await matcher.evaluate(profile, requirement)
    assert res.requirement_id == "REQ1"
    # Since Containerization is in profile.skills, it should exact match
    assert res.matching_method == "canonical"
    assert res.matched_skill == "Containerization"
    assert res.status == MatchStatus.SATISFIED or res.status == MatchStatus.PARTIAL
