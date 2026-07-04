import pytest
from app.services.impl.skill_normalizer_service_impl import SkillNormalizerServiceImpl
from app.schemas.skill_normalizer import NormalizedSkill

@pytest.mark.asyncio
async def test_clean_text():
    # We can instantiate the service directly. We pass None for DB session
    # since we only test synchronous text cleaning logic first.
    normalizer = SkillNormalizerServiceImpl(db=None)
    assert normalizer._clean_text("FastAPI (Python Framework)") == "fastapi"
    assert normalizer._clean_text("  Docker Compose  ") == "docker compose"
    assert normalizer._clean_text(None) == ""

@pytest.mark.asyncio
async def test_normalize_dictionary_and_alias(db_session):
    normalizer = SkillNormalizerServiceImpl(db=db_session)
    
    # Test Exact alias mapping: js -> javascript
    res = await normalizer.normalize("js")
    assert res.normalized == "js"
    assert res.canonical == "Frontend Development"

    
    # Test Exact Canonical mapping: fastapi -> Backend Development
    res2 = await normalizer.normalize("fastapi")
    assert res2.canonical == "Backend Development"
    assert res2.mapping_method == "dictionary"
