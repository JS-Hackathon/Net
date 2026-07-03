"""Versioned prompt definitions for AI job matching.

Prompts are kept out of service code (see AI Principles: never hardcode prompts
inside services). Each prompt carries a version and the exact JSON schema the model
must return so responses can be validated before persistence.
"""
import json
from typing import Dict, Any

JOB_MATCHING_PROMPT_VERSION = "1.0"

_SYSTEM_INSTRUCTION = (
    "You are an expert career counselor and technical recruiter analyzing "
    "job-candidate compatibility. Analyze the candidate profile against the job "
    "requirements and return a detailed, structured assessment. "
    "Be thorough but concise. Return ONLY raw JSON, no markdown fences."
)

# The exact JSON shape the model must produce.
_RESPONSE_SCHEMA_HINT = """
{
  "overall_assessment": {
    "match_score": number,        // 0-100 overall compatibility
    "confidence": number,          // 0-100 confidence in this assessment
    "summary": "string"
  },
  "skills_analysis": {
    "matching_skills": [
      {"skill": "string", "candidate_level": "string", "required_level": "string", "match_quality": "excellent|good|fair"}
    ],
    "missing_skills": [
      {"skill": "string", "required_level": "string", "importance": "critical|high|medium", "learning_effort": "low|medium|high"}
    ],
    "bonus_skills": [
      {"skill": "string", "value": "string"}
    ],
    "skills_score": number         // 0-100
  },
  "experience_analysis": {
    "relevant_experience": "string",
    "experience_gaps": ["string"],
    "experience_score": number,    // 0-100
    "career_progression_fit": "string"
  },
  "education_analysis": {
    "education_fit": "string",
    "education_score": number,     // 0-100
    "additional_education_needs": ["string"]
  },
  "location_compatibility": {
    "location_score": number,      // 0-100
    "remote_work_fit": "string",
    "relocation_considerations": "string"
  },
  "strengths": ["string"],
  "areas_for_improvement": [
    {"area": "string", "priority": "high|medium|low", "suggestion": "string"}
  ],
  "recommendation": {
    "should_apply": boolean,
    "likelihood_of_success": "high|medium|low",
    "key_selling_points": ["string"],
    "preparation_advice": "string"
  }
}
""".strip()


def build_matching_prompt(candidate: Dict[str, Any], job: Dict[str, Any]) -> str:
    """Assemble the full matching prompt from candidate + job structured data."""
    return (
        f"{_SYSTEM_INSTRUCTION}\n\n"
        "Analyze this candidate's fit for the job position and provide a detailed "
        "matching assessment.\n\n"
        f"CANDIDATE PROFILE:\n{json.dumps(candidate, ensure_ascii=False, default=str)}\n\n"
        f"JOB REQUIREMENTS:\n{json.dumps(job, ensure_ascii=False, default=str)}\n\n"
        f"Return the analysis in EXACTLY this JSON format:\n{_RESPONSE_SCHEMA_HINT}"
    )
