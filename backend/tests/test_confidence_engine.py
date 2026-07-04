import pytest
from app.services.impl.confidence_engine_service_impl import ConfidenceEngineServiceImpl
from app.schemas.job_matching import RequirementMatch, MatchEvidence
from app.enums.match_status import MatchStatus

@pytest.mark.asyncio
async def test_confidence_scoring_exact():
    engine = ConfidenceEngineServiceImpl()
    
    # Test perfect exact canonical match with multiple evidences
    match_result = RequirementMatch(
        requirement="Containerization",
        matched_skill="Docker",
        matching_method="canonical",
        semantic_similarity=1.0,
        evidence=[
            MatchEvidence(section="skills", text="Docker"),
            MatchEvidence(section="experience", text="Managed Docker environments"),
            MatchEvidence(section="projects", text="Built Docker containers")
        ]
    )
    
    res = await engine.score(match_result)
    assert res.confidence >= 0.90
    assert res.status == MatchStatus.SATISFIED
    assert "Exact canonical match found." in res.reasoning

@pytest.mark.asyncio
async def test_confidence_scoring_missing():
    engine = ConfidenceEngineServiceImpl()
    
    # Test missing match with no evidence
    match_result = RequirementMatch(
        requirement="Containerization",
        matched_skill="None",
        matching_method="none",
        semantic_similarity=0.0,
        evidence=[]
    )
    
    res = await engine.score(match_result)
    assert res.confidence == 0.0
    assert res.status == MatchStatus.MISSING
    assert "No active evidence found in the CV." in res.reasoning
