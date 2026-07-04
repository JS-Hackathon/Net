from pydantic import BaseModel, Field
from typing import Literal
from app.enums.requirement_priority import RequirementPriority
from app.enums.match_status import MatchStatus

class ProfileSkill(BaseModel):
    canonical: str = Field(..., description="Canonical skill name.")
    category: str = Field(..., description="High-level skill category.")
    confidence: float = Field(..., ge=0.0, le=1.0)
    mapping_method: str = Field(..., description="How the skill was mapped.")

class ProfileExperience(BaseModel):
    title: str
    company: str
    duration_months: int
    description: str

class ProfileProject(BaseModel):
    name: str
    description: str
    technologies: list[str] = Field(default_factory=list)

class CandidateProfileInput(BaseModel):
    user_id: str
    skills: list[ProfileSkill] = Field(default_factory=list)
    experience: list[ProfileExperience] = Field(default_factory=list)
    projects: list[ProfileProject] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    summary: str = Field(default="")

class JobRequirement(BaseModel):
    id: str = Field(..., description="Unique requirement identifier within the JD.")
    text: str = Field(..., description="Raw requirement text from JD.")
    canonical: str = Field(..., description="Canonical form of skill requirement.")
    category: str = Field(..., description="Skill category.")
    section: Literal["must_have", "required", "preferred", "nice_to_have"] = Field(
        ..., description="JD section this requirement belongs to."
    )
    priority: RequirementPriority = Field(
        ..., description="Business importance derived from section."
    )

class PriorityInfo(BaseModel):
    level: RequirementPriority
    score: float = Field(..., ge=0.0, le=1.0)

class MatchEvidence(BaseModel):
    section: str = Field(..., description="CV section: skills, experience, projects, certifications, summary.")
    text: str = Field(..., description="Raw text snippet supporting the match.")

class RequirementMatch(BaseModel):
    requirement: str = Field(..., description="Canonical skill required by the JD.")
    matched_skill: str = Field(..., description="Canonical skill found in the candidate profile.")
    matching_method: str = Field(..., description="canonical | alias | ai | cached | none")
    semantic_similarity: float = Field(..., ge=0.0, le=1.0)
    evidence: list[MatchEvidence] = Field(default_factory=list)


class RequirementMatchResult(BaseModel):
    requirement_id: str = Field(..., description="Unique ID of the requirement.")
    requirement: str = Field(..., description="Canonical skill required by the JD.")
    status: MatchStatus = Field(..., description="Requirement satisfaction status.")
    priority: PriorityInfo = Field(..., description="Requirement priority and score.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence from ConfidenceEngineService.")
    evidence_score: float = Field(..., ge=0.0, le=1.0, description="Aggregated evidence strength.")
    matched_skill: str = Field(..., description="Candidate canonical skill matched against requirement.")
    matching_method: str = Field(..., description="canonical | alias | ai | cached | none")
    evidence: list[MatchEvidence] = Field(default_factory=list)
    reasoning: list[str] = Field(..., description="Human-readable explanation of the match decision.")
    contribution: float = Field(
        ..., ge=0.0, le=1.0,
        description="Weighted contribution to overall match score. = priority.score * confidence"
    )

# Request schema for matching endpoint
class CompareRequest(BaseModel):
    candidate_profile_id: str = Field(..., description="Candidate Profile UUID.")
    job_id: str = Field(..., description="Job ID (e.g. from JSearch).")
    job_title: str = Field(..., description="Job title.")
    company_name: str = Field(..., description="Company name.")
    requirements: list[JobRequirement] = Field(..., description="List of job requirements extracted from JD.")

# Response schema for matching endpoint
class CompareResponse(BaseModel):
    match_id: str = Field(..., description="Saved JobMatch UUID.")
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Overall match score (0-100).")
    match_matrix: list[RequirementMatchResult] = Field(..., description="Matrix of all requirement evaluations.")
