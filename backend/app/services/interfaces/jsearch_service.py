from typing import Protocol, List, Dict, Any, Optional

class JSearchService(Protocol):
    async def search_jobs(
        self,
        query: str,
        page: int = 1,
        *,
        country: Optional[str] = None,
        date_posted: Optional[str] = None,
        remote_only: bool = False,
        employment_types: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search for jobs matching the query.

        Args:
            query (str): Job title, keywords, or location.
            page (int): Page number for pagination.
            country (Optional[str]): ISO country code (e.g. "vn", "us"). Defaults to settings.
            date_posted (Optional[str]): all | today | 3days | week | month. Defaults to settings.
            remote_only (bool): Only work-from-home jobs (JSearch work_from_home).
            employment_types (Optional[str]): Comma list, e.g. "FULLTIME,INTERN".

        Returns:
            List[Dict[str, Any]]: List of matching jobs.
        """
        ...
