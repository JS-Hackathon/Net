from pydantic import BaseModel, Field
from typing import Literal

class NormalizedSkill(BaseModel):
    raw: str = Field(..., description="Original skill string as extracted from CV or JD.")
    normalized: str = Field(..., description="Cleaned, lowercased version before canonical mapping.")
    canonical: str = Field(..., description="Final canonical skill name.")
    category: str = Field(..., description="High-level skill category (e.g., DevOps, Backend Development).")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score of the mapping.")
    mapping_method: Literal["dictionary", "alias", "ai", "cached"] = Field(
        ..., description="Method used to produce this mapping."
    )
