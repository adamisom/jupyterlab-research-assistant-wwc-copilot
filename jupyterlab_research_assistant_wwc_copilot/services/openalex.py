"""OpenAlex API client for paper discovery."""

import time
from typing import Optional

import requests


class OpenAlexAPI:
    """Client for interacting with the OpenAlex API."""

    BASE_URL = "https://api.openalex.org"

    def __init__(self):
        """Initialize the OpenAlex API client."""
        self.session = requests.Session()
        self.last_request_time = 0
        self.min_request_interval = 0.1  # OpenAlex is more lenient with rate limits

    def _rate_limit(self):
        """Simple rate limiting to avoid hitting API limits."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()

    def search_papers(
        self, query: str, year: Optional[str] = None, limit: int = 20, offset: int = 0
    ) -> dict:
        """
        Search for papers using OpenAlex API.

        Args:
            query: Search query string
            year: Year filter (e.g., "2015-2024" or "2020")
            limit: Maximum number of results (default 20, max 200)
            offset: Pagination offset

        Returns:
            Dictionary with 'data' (list of papers) and 'total' (total count)

        Raises:
            Exception: If API request fails
        """
        self._rate_limit()

        # OpenAlex uses a search string format
        search_query = query

        # Add year filter if provided
        if year:
            # Parse year range (e.g., "2015-2024" or "2020")
            if "-" in year:
                start_year, end_year = year.split("-", 1)
                search_query = f"{query},publication_year:{start_year}-{end_year}"
            else:
                search_query = f"{query},publication_year:{year}"

        params = {
            "search": search_query,
            "per_page": min(limit, 200),  # OpenAlex max is 200
            "page": (offset // min(limit, 200)) + 1,  # OpenAlex uses page numbers
            "sort": "relevance_score:desc",  # Sort by relevance
        }

        try:
            response = self.session.get(
                f"{self.BASE_URL}/works", params=params, timeout=10
            )
            response.raise_for_status()
            data = response.json()

            # Transform to our format (matching Semantic Scholar format)
            papers = []
            for work in data.get("results", []):
                # Extract authors (as strings to match IPaper interface)
                authors = []
                for author in work.get("authorships", [])[
                    :10
                ]:  # Limit to first 10 authors
                    author_name = author.get("author", {}).get("display_name", "")
                    if author_name:
                        authors.append(author_name)

                # Extract PDF URL
                open_access = work.get("open_access", {})
                pdf_url = None
                if open_access.get("is_oa"):
                    # Try to get PDF from primary_location
                    primary_location = work.get("primary_location", {})
                    if primary_location:
                        pdf_url = primary_location.get("pdf_url")

                papers.append(
                    {
                        "paperId": work.get("id", "").split("/")[-1]
                        if work.get("id")
                        else None,  # Extract ID from URL
                        "title": work.get("title", ""),
                        "authors": authors,
                        "year": work.get("publication_year"),
                        "abstract": work.get("abstract", ""),
                        "doi": work.get("doi", "").replace("https://doi.org/", "")
                        if work.get("doi")
                        else None,
                        "citation_count": work.get("cited_by_count", 0),
                        "open_access_pdf": pdf_url,
                    }
                )

            return {
                "data": papers,
                "total": data.get("meta", {}).get("count", len(papers)),
            }
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
            raise RuntimeError(f"OpenAlex API error: {error_msg}") from e
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"OpenAlex API error: {e!s}") from e

    def get_paper_details(self, paper_id: str) -> Optional[dict]:
        """
        Fetch detailed information for a single paper by OpenAlex ID.

        Args:
            paper_id: OpenAlex work ID (can be full URL or just ID)

        Returns:
            Paper details dictionary or None if not found

        Raises:
            Exception: If API request fails
        """
        self._rate_limit()

        # OpenAlex IDs can be full URLs or just the ID part
        if paper_id.startswith("http"):
            work_id = paper_id
        else:
            work_id = f"https://openalex.org/W{paper_id}"

        try:
            response = self.session.get(work_id, params={"format": "json"}, timeout=10)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            work = response.json()

            # Extract authors (as strings to match IPaper interface)
            authors = []
            for author in work.get("authorships", []):
                author_name = author.get("author", {}).get("display_name", "")
                if author_name:
                    authors.append(author_name)

            # Extract PDF URL
            open_access = work.get("open_access", {})
            pdf_url = None
            if open_access.get("is_oa"):
                primary_location = work.get("primary_location", {})
                if primary_location:
                    pdf_url = primary_location.get("pdf_url")

            return {
                "paperId": work.get("id", "").split("/")[-1]
                if work.get("id")
                else None,
                "title": work.get("title", ""),
                "authors": authors,
                "year": work.get("publication_year"),
                "abstract": work.get("abstract", ""),
                "doi": work.get("doi", "").replace("https://doi.org/", "")
                if work.get("doi")
                else None,
                "citation_count": work.get("cited_by_count", 0),
                "reference_count": len(work.get("referenced_works", [])),
                "open_access_pdf": pdf_url,
            }
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"OpenAlex API error: {e!s}") from e
