from typing import Protocol, Dict, Any

class AIProvider(Protocol):
    async def parse_resume(self, text: str) -> Dict[str, Any]:
        """Parse resume text into a structured candidate profile JSON.

        Args:
            text (str): Raw text extracted from the resume.

        Returns:
            Dict[str, Any]: Structured candidate profile containing skills, experience, education, etc.
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
