from typing import Protocol, List, Dict, Any, Optional

class JSearchService(Protocol):
    async def search_jobs(
        self, query: str, page: int = 1, country: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for jobs matching the query.

        Args:
            query (str): Job title, keywords, or location.
            page (int): Page number for pagination (search-v2 uses num_pages; kept for compatibility).
            country (Optional[str]): ISO country code (e.g. "vn", "us"). Defaults to settings.

        Returns:
            List[Dict[str, Any]]: List of matching jobs.
        """
        ...
