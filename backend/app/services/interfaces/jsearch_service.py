from typing import Protocol, List, Dict, Any

class JSearchService(Protocol):
    async def search_jobs(self, query: str, page: int = 1) -> List[Dict[str, Any]]:
        """Search for jobs matching the query.

        Args:
            query (str): Job title, keywords, or location.
            page (int): Page number for pagination.

        Returns:
            List[Dict[str, Any]]: List of matching jobs.
        """
        ...
