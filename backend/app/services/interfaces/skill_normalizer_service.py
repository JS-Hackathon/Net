from typing import Protocol
from app.schemas.skill_normalizer import NormalizedSkill

class ISkillNormalizerService(Protocol):
    async def normalize(self, skill: str) -> NormalizedSkill:
        """Normalize a single raw skill string into a canonical representation.

        Args:
            skill (str): Raw skill string extracted from a CV or JD.

        Returns:
            NormalizedSkill: Canonical name, category, confidence, mapping method.
        """
        ...

    async def normalize_batch(self, skills: list[str]) -> list[NormalizedSkill]:
        """Normalize a list of raw skill strings.

        Args:
            skills (list[str]): Raw skill strings.

        Returns:
            list[NormalizedSkill]: List of normalized outputs.
        """
        ...
