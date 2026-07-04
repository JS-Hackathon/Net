"""Prompt + structured-output schema for parsing an uploaded Job Description
(JD) file into a structured job — mirrors the resume parser, but the output
maps onto the `jobs` table so an uploaded JD becomes searchable/matchable just
like a crawled job."""

JD_PARSE_PROMPT_VERSION = "jd-parse-1.0"

# Gemini structured-output schema (OpenAPI subset; UPPERCASE types).
JOB_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "title": {"type": "STRING", "nullable": True},
        "company_name": {"type": "STRING", "nullable": True},
        "location": {"type": "STRING", "nullable": True},
        # remote | hybrid | on-site | fulltime | parttime | contract | internship
        "employment_type": {"type": "STRING", "nullable": True},
        "experience_level": {"type": "STRING", "nullable": True},  # entry | mid | senior
        "salary_min": {"type": "INTEGER", "nullable": True},
        "salary_max": {"type": "INTEGER", "nullable": True},
        "salary_currency": {"type": "STRING", "nullable": True},
        "description": {"type": "STRING", "nullable": True},
        "requirements": {"type": "STRING", "nullable": True},
        "benefits": {"type": "STRING", "nullable": True},
        "skills_required": {"type": "ARRAY", "items": {"type": "STRING"}},
        "industry": {"type": "STRING", "nullable": True},
    },
    "required": ["title"],
}

_INSTRUCTION = (
    "You are an expert recruiter. Extract the following JOB DESCRIPTION into the "
    "provided JSON schema.\n"
    "Rules:\n"
    "- Preserve the JD's ORIGINAL language (do not translate).\n"
    "- If a field is absent, use null (or an empty array for skills). Never invent data.\n"
    "- salary_min/salary_max must be INTEGERS (numeric only, no currency text).\n"
    "- skills_required: concrete technologies/skills required (e.g. Python, React, AWS).\n"
    "- experience_level: map to entry | mid | senior when it can be inferred.\n"
)


def build_jd_text_prompt(jd_text: str) -> str:
    """Prompt for the text path (extracted plain text). Capped for token safety."""
    text = (jd_text or "")[:18000]
    return f"{_INSTRUCTION}\nJob Description:\n{text}"


def build_jd_pdf_prompt() -> str:
    """Instruction for the multimodal path (a scanned/image JD PDF is attached)."""
    return (
        f"{_INSTRUCTION}\nThe job description is attached as a PDF (it may be a "
        "scanned image). Read the document, including any image/scanned text, and "
        "extract the fields."
    )
