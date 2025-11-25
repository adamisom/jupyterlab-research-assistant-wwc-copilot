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
            ),
        }
        if include_references:
            result["reference_count"] = paper.get("referenceCount", 0)
        return result

    def search_papers(
        self,
        query: str,
        year: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        """
        Search for papers using Semantic Scholar API.

        Args:
            query: Search query string
            year: Year filter (e.g., "2015-2024" or "2020") - applied client-side
            limit: Maximum number of results (default 20, max 100)
            offset: Pagination offset

        Returns:
            Dictionary with 'data' (list of papers) and 'total' (total count)

        Raises:
            Exception: If API request fails
        """
        self._rate_limit()

        # Note: Semantic Scholar API /paper/search endpoint doesn't support year parameter
        # Year filtering is done client-side after fetching results
        # Using minimal fields to avoid API errors - can expand later if needed
        params = {
            "query": query,
            "limit": min(limit, 100),  # API max is 100
            "offset": offset,
            "fields": "title,authors,year,abstract,doi,paperId,citationCount",
        }
        # Removed: if year: params["year"] = year

        try:
            response = self.session.get(
                f"{self.BASE_URL}/paper/search", params=params, timeout=10
            )
            response.raise_for_status()
            data = response.json()

            # Transform to our format
            papers = [self._transform_paper(paper) for paper in data.get("data", [])]

            # Client-side year filtering (Semantic Scholar API doesn't support year parameter)
            if year:
                filtered_papers = []
                if "-" in year:
                    # Year range (e.g., "2020-2024")
                    try:
                        start_year, end_year = year.split("-", 1)
                        start_year_int = int(start_year.strip())
                        end_year_int = int(end_year.strip())
                        for paper in papers:
                            paper_year = paper.get("year")
                            if paper_year and start_year_int <= paper_year <= end_year_int:
                                filtered_papers.append(paper)
                    except (ValueError, AttributeError):
                        # Invalid year range format, return all papers
                        filtered_papers = papers
                else:
                    # Single year (e.g., "2020")
                    try:
                        year_int = int(year.strip())
                        for paper in papers:
                            if paper.get("year") == year_int:
                                filtered_papers.append(paper)
                    except (ValueError, AttributeError):
                        # Invalid year format, return all papers
                        filtered_papers = papers
                papers = filtered_papers

            return {"data": papers, "total": len(papers)}
        except requests.exceptions.HTTPError as e:
            # Include response body for better error messages
            error_msg = str(e)
            try:
                if hasattr(e, "response") and e.response is not None:
                    error_detail = e.response.json()
                    if error_detail:
                        error_msg = f"{error_msg} - Response: {error_detail}"
            except Exception:
                pass
            raise RuntimeError(f"Semantic Scholar API error: {error_msg}") from e
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
                f"{self.BASE_URL}/paper/{paper_id}", params=params, timeout=10
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            paper = response.json()

            return self._transform_paper(paper, include_references=True)
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Semantic Scholar API error: {e!s}") from e
