from typing import Protocol, Dict, Any

class AIProvider(Protocol):
    async def parse_resume(self, text: str, pdf_bytes: bytes | None = None) -> Dict[str, Any]:
        """Parse a resume into a structured candidate profile JSON.

        Args:
            text (str): Raw text extracted from the resume (normal path).
            pdf_bytes (bytes | None): Raw PDF bytes for the multimodal/OCR path,
                used when text extraction yields nothing (scanned/image CV).

        Returns:
            Dict[str, Any]: Structured candidate profile (personal_info, work
                experience, education, skills, etc.).
        """
        ...
    
    async def match_job(self, profile: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        """Compare a candidate profile with a job description.

        Args:
            profile (Dict[str, Any]): Candidate profile JSON.
            job (Dict[str, Any]): Job description JSON.

        Returns:
            Dict[str, Any]: Match result with score, strengths, weaknesses, etc.
        """
        ...
