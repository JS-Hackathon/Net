"""Prompt + structured-output schema for resume parsing.

Kept separate from the provider so the canonical output schema is the single
source of truth. The schema mirrors the CandidateProfile shape so the parsed
result maps cleanly onto the profile (previously the prompt omitted
personal_info entirely, leaving every profile without name/email/phone).
"""

RESUME_PARSE_PROMPT_VERSION = "resume-parse-2.0"

# Google Gemini structured-output schema (OpenAPI subset: types are UPPERCASE,
# optional fields marked nullable). Forcing this schema removes the schema drift
# the old free-form prompt caused.
RESUME_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "personal_info": {
            "type": "OBJECT",
            "properties": {
                "full_name": {"type": "STRING", "nullable": True},
                "email": {"type": "STRING", "nullable": True},
                "phone": {"type": "STRING", "nullable": True},
                "location": {"type": "STRING", "nullable": True},
                "linkedin_url": {"type": "STRING", "nullable": True},
                "portfolio_url": {"type": "STRING", "nullable": True},
                "github_url": {"type": "STRING", "nullable": True},
                "website_url": {"type": "STRING", "nullable": True},
            },
        },
        "professional_summary": {"type": "STRING", "nullable": True},
        "career_objective": {"type": "STRING", "nullable": True},
        "years_of_experience": {"type": "INTEGER", "nullable": True},
        "current_role": {"type": "STRING", "nullable": True},
        "current_company": {"type": "STRING", "nullable": True},
        "work_experience": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "title": {"type": "STRING", "nullable": True},
                    "company": {"type": "STRING", "nullable": True},
                    "location": {"type": "STRING", "nullable": True},
                    "start_date": {"type": "STRING", "nullable": True},
                    "end_date": {"type": "STRING", "nullable": True},
                    "is_current": {"type": "BOOLEAN", "nullable": True},
                    "description": {"type": "STRING", "nullable": True},
                    "key_achievements": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "technologies_used": {"type": "ARRAY", "items": {"type": "STRING"}},
                },
            },
        },
        "education": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "degree": {"type": "STRING", "nullable": True},
                    "field_of_study": {"type": "STRING", "nullable": True},
                    "institution": {"type": "STRING", "nullable": True},
                    "location": {"type": "STRING", "nullable": True},
                    "graduation_date": {"type": "STRING", "nullable": True},
                    "gpa": {"type": "STRING", "nullable": True},
                    "honors": {"type": "ARRAY", "items": {"type": "STRING"}},
                },
            },
        },
        "technical_skills": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "name": {"type": "STRING", "nullable": True},
                    "category": {"type": "STRING", "nullable": True},
                    "proficiency": {"type": "STRING", "nullable": True},
                    "years_experience": {"type": "INTEGER", "nullable": True},
                },
            },
        },
        "soft_skills": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "name": {"type": "STRING", "nullable": True},
                    "description": {"type": "STRING", "nullable": True},
                },
            },
        },
        "certifications": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "name": {"type": "STRING", "nullable": True},
                    "issuer": {"type": "STRING", "nullable": True},
                    "issue_date": {"type": "STRING", "nullable": True},
                    "expiry_date": {"type": "STRING", "nullable": True},
                    "credential_id": {"type": "STRING", "nullable": True},
                    "verification_url": {"type": "STRING", "nullable": True},
                },
            },
        },
        "languages": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "language": {"type": "STRING", "nullable": True},
                    "proficiency": {"type": "STRING", "nullable": True},
                },
            },
        },
        "projects": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "name": {"type": "STRING", "nullable": True},
                    "description": {"type": "STRING", "nullable": True},
                    "technologies": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "url": {"type": "STRING", "nullable": True},
                    "start_date": {"type": "STRING", "nullable": True},
                    "end_date": {"type": "STRING", "nullable": True},
                },
            },
        },
        "achievements": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "title": {"type": "STRING", "nullable": True},
                    "description": {"type": "STRING", "nullable": True},
                    "date": {"type": "STRING", "nullable": True},
                    "issuer": {"type": "STRING", "nullable": True},
                },
            },
        },
    },
    "required": ["personal_info"],
}

_INSTRUCTION = (
    "You are an expert resume/CV parser. Extract the candidate's information into "
    "the provided JSON schema.\n"
    "Rules:\n"
    "- Preserve the resume's ORIGINAL language (do not translate).\n"
    "- If a field is not present in the resume, use null (or an empty array for lists). "
    "Never invent or guess data.\n"
    "- `years_of_experience` must be an INTEGER (total professional years, rounded).\n"
    "- Extract personal_info (name, email, phone, location, links) whenever present — "
    "this is the most important section.\n"
    "- `languages` means SPOKEN/human languages (e.g. English, Vietnamese). Do NOT "
    "put programming languages there — those belong in technical_skills.\n"
)


# Cap the extracted text sent to the model. A resume is short; this guards
# against pathological inputs blowing up token usage (cost/quota) on free tier.
MAX_RESUME_TEXT_CHARS = 18000


def build_resume_text_prompt(resume_text: str) -> str:
    """Prompt for the text path (extracted plain text)."""
    text = (resume_text or "")[:MAX_RESUME_TEXT_CHARS]
    return f"{_INSTRUCTION}\nResume Text:\n{text}"


def build_resume_pdf_prompt() -> str:
    """Instruction for the multimodal path (the PDF file is attached separately).

    Used when text extraction yields almost nothing (scanned/image PDF) — Gemini
    reads the document directly, including image/scanned text.
    """
    return (
        f"{_INSTRUCTION}\nThe resume is attached as a PDF document (it may be a "
        "scanned image). Read the document, including any image/scanned text, and "
        "extract the fields."
    )
