"""Tests for Semantic Scholar API client."""

from unittest.mock import Mock, patch

import pytest

from jupyterlab_research_assistant_wwc_copilot.services.semantic_scholar import (
    SemanticScholarAPI,
)


def test_rate_limiting():
    """Test that rate limiting is applied."""
    api = SemanticScholarAPI()
    initial_time = api.last_request_time
    api._rate_limit()
    assert api.last_request_time >= initial_time


@patch(
    "jupyterlab_research_assistant_wwc_copilot.services.semantic_scholar.requests.Session"
)
def test_search_papers_success(mock_session_class):
    """Test successful paper search."""
    # Mock the session and response
    mock_session = Mock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "data": [
            {
                "paperId": "123",
                "title": "Test Paper",
                "authors": [{"name": "Author 1"}],
                "year": 2023,
                "abstract": "Test abstract",
                "doi": "10.1234/test",
                "citationCount": 10,
                "openAccessPdf": None,
            }
        ],
        "total": 1,
    }
    mock_response.raise_for_status = Mock()
    mock_session.get.return_value = mock_response
    mock_session_class.return_value = mock_session

    api = SemanticScholarAPI()
    results = api.search_papers("test query")

    assert results["total"] == 1
    assert len(results["data"]) == 1
    assert results["data"][0]["title"] == "Test Paper"
    assert results["data"][0]["paperId"] == "123"


@patch(
    "jupyterlab_research_assistant_wwc_copilot.services.semantic_scholar.requests.Session"
)
def test_search_papers_with_year(mock_session_class):
    """Test paper search with year filter."""
    mock_session = Mock()
    mock_response = Mock()
    mock_response.json.return_value = {"data": [], "total": 0}
    mock_response.raise_for_status = Mock()
    mock_session.get.return_value = mock_response
    mock_session_class.return_value = mock_session

    api = SemanticScholarAPI()
    api.search_papers("test", year="2020-2024")

    # Verify year parameter was passed
    call_args = mock_session.get.call_args
    assert "year" in call_args[1]["params"]
    assert call_args[1]["params"]["year"] == "2020-2024"


@patch(
    "jupyterlab_research_assistant_wwc_copilot.services.semantic_scholar.requests.Session"
)
def test_search_papers_error(mock_session_class):
    """Test error handling in paper search."""
    import requests

    mock_session = Mock()
    # Use requests.exceptions.RequestException to match the actual exception type
    mock_session.get.side_effect = requests.exceptions.RequestException("Network error")
    mock_session_class.return_value = mock_session

    api = SemanticScholarAPI()
    with pytest.raises(Exception) as exc_info:
        api.search_papers("test")
    assert "Semantic Scholar API error" in str(exc_info.value)


@patch(
    "jupyterlab_research_assistant_wwc_copilot.services.semantic_scholar.requests.Session"
)
def test_get_paper_details_success(mock_session_class):
    """Test successful paper details retrieval."""
    mock_session = Mock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "paperId": "123",
        "title": "Test Paper",
        "authors": [{"name": "Author 1"}],
        "year": 2023,
        "abstract": "Test abstract",
        "doi": "10.1234/test",
        "citationCount": 10,
        "referenceCount": 5,
        "openAccessPdf": None,
    }
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()
    mock_session.get.return_value = mock_response
    mock_session_class.return_value = mock_session

    api = SemanticScholarAPI()
    result = api.get_paper_details("123")

    assert result is not None
    assert result["title"] == "Test Paper"
    assert result["paperId"] == "123"
    assert result["reference_count"] == 5


@patch(
    "jupyterlab_research_assistant_wwc_copilot.services.semantic_scholar.requests.Session"
)
def test_get_paper_details_not_found(mock_session_class):
    """Test handling of paper not found."""
    mock_session = Mock()
    mock_response = Mock()
    mock_response.status_code = 404
    mock_session.get.return_value = mock_response
    mock_session_class.return_value = mock_session

    api = SemanticScholarAPI()
    result = api.get_paper_details("nonexistent")

    assert result is None
