"""Semantic Scholar API client for paper discovery."""

import time
from typing import Optional

import requests


class SemanticScholarAPI:
    """Client for interacting with the Semantic Scholar API."""

    BASE_URL = "https://api.semanticscholar.org/graph/v1"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Semantic Scholar API client.

        Args:
            api_key: Optional API key for higher rate limits
        """
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"x-api-key": api_key})
        self.last_request_time = 0
        self.min_request_interval = 0.3  # 300ms between requests (conservative)

    def _rate_limit(self):
        """Simple rate limiting to avoid hitting API limits."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()

    def _transform_paper(self, paper: dict, include_references: bool = False) -> dict:
        """
        Transform Semantic Scholar paper format to our internal format.

        Args:
            paper: Paper dictionary from Semantic Scholar API
            include_references: Whether to include reference_count field

        Returns:
            Transformed paper dictionary
        """
        result = {
            "paperId": paper.get("paperId"),
            "title": paper.get("title", ""),
            "authors": [a.get("name", "") for a in paper.get("authors", [])],
            "year": paper.get("year"),
            "abstract": paper.get("abstract", ""),
            "doi": paper.get("doi"),
            "citation_count": paper.get("citationCount", 0),
            "open_access_pdf": (
                paper.get("openAccessPdf", {}).get("url")
                if paper.get("openAccessPdf")
                else None
            )
        }
        if include_references:
            result["reference_count"] = paper.get("referenceCount", 0)
        return result

    def search_papers(
        self,
        query: str,
        year: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> dict:
        """
        Search for papers using Semantic Scholar API.

        Args:
            query: Search query string
            year: Year filter (e.g., "2015-2024" or "2020")
            limit: Maximum number of results (default 20, max 100)
            offset: Pagination offset

        Returns:
            Dictionary with 'data' (list of papers) and 'total' (total count)

        Raises:
            Exception: If API request fails
        """
        self._rate_limit()

        params = {
            "query": query,
            "limit": min(limit, 100),  # API max is 100
            "offset": offset,
            "fields": (
                "title,authors,year,abstract,doi,openAccessPdf,"
                "paperId,citationCount"
            )
        }

        if year:
            params["year"] = year

        try:
            response = self.session.get(
                f"{self.BASE_URL}/paper/search",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            # Transform to our format
            papers = [
                self._transform_paper(paper)
                for paper in data.get("data", [])
            ]

            return {
                "data": papers,
                "total": data.get("total", len(papers))
            }
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Semantic Scholar API error: {e!s}") from e

    def get_paper_details(self, paper_id: str) -> Optional[dict]:
        """
        Fetch detailed information for a single paper by Semantic Scholar ID.

        Args:
            paper_id: Semantic Scholar paper ID

        Returns:
            Paper details dictionary or None if not found

        Raises:
            Exception: If API request fails
        """
        self._rate_limit()

        params = {
            "fields": (
                "title,authors,year,abstract,doi,openAccessPdf,"
                "paperId,citationCount,referenceCount"
            )
        }

        try:
            response = self.session.get(
                f"{self.BASE_URL}/paper/{paper_id}",
                params=params,
                timeout=10
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            paper = response.json()

            return self._transform_paper(paper, include_references=True)
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Semantic Scholar API error: {e!s}") from e

