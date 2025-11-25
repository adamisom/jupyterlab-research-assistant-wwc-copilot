"""Tests for OpenAlex API client."""

from unittest.mock import Mock, patch

import pytest

from jupyterlab_research_assistant_wwc_copilot.services.openalex import OpenAlexAPI


def test_rate_limiting():
    """Test that rate limiting is applied."""
    api = OpenAlexAPI()
    initial_time = api.last_request_time
    api._rate_limit()
    assert api.last_request_time >= initial_time


@patch("jupyterlab_research_assistant_wwc_copilot.services.openalex.requests.Session")
def test_search_papers_success(mock_session_class):
    """Test successful paper search."""
    # Mock the session and response
    mock_session = Mock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "results": [
            {
                "id": "https://openalex.org/W123",
                "title": "Test Paper",
                "authorships": [
                    {"author": {"display_name": "Author 1"}},
                    {"author": {"display_name": "Author 2"}},
                ],
                "publication_year": 2023,
                "abstract": "Test abstract",
                "doi": "https://doi.org/10.1234/test",
                "cited_by_count": 10,
                "open_access": {"is_oa": True},
                "primary_location": {"pdf_url": "https://example.com/paper.pdf"},
            }
        ],
        "meta": {"count": 1},
    }
    mock_response.raise_for_status = Mock()
    mock_session.get.return_value = mock_response
    mock_session_class.return_value = mock_session

    api = OpenAlexAPI()
    results = api.search_papers("test query")

    assert results["total"] == 1
    assert len(results["data"]) == 1
    assert results["data"][0]["title"] == "Test Paper"
    assert results["data"][0]["paperId"] == "W123"
    assert results["data"][0]["authors"] == ["Author 1", "Author 2"]
    assert results["data"][0]["year"] == 2023


@patch("jupyterlab_research_assistant_wwc_copilot.services.openalex.requests.Session")
def test_search_papers_with_year(mock_session_class):
    """Test paper search with year filter."""
    mock_session = Mock()
    mock_response = Mock()
    mock_response.json.return_value = {"results": [], "meta": {"count": 0}}
    mock_response.raise_for_status = Mock()
    mock_session.get.return_value = mock_response
    mock_session_class.return_value = mock_session

    api = OpenAlexAPI()
    api.search_papers("test", year="2020-2024")

    # Verify year was included in search query
    call_args = mock_session.get.call_args
    assert "publication_year:2020-2024" in call_args[1]["params"]["search"]


@patch("jupyterlab_research_assistant_wwc_copilot.services.openalex.requests.Session")
def test_search_papers_error(mock_session_class):
    """Test error handling in paper search."""
    import requests

    mock_session = Mock()
    mock_session.get.side_effect = requests.exceptions.RequestException("Network error")
    mock_session_class.return_value = mock_session

    api = OpenAlexAPI()
    with pytest.raises(Exception) as exc_info:
        api.search_papers("test")
    assert "OpenAlex API error" in str(exc_info.value)


@patch("jupyterlab_research_assistant_wwc_copilot.services.openalex.requests.Session")
def test_get_paper_details_success(mock_session_class):
    """Test successful paper details retrieval."""
    mock_session = Mock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "id": "https://openalex.org/W123",
        "title": "Test Paper",
        "authorships": [{"author": {"display_name": "Author 1"}}],
        "publication_year": 2023,
        "abstract": "Test abstract",
        "doi": "https://doi.org/10.1234/test",
        "cited_by_count": 10,
        "referenced_works": ["ref1", "ref2"],
        "open_access": {"is_oa": True},
        "primary_location": {"pdf_url": "https://example.com/paper.pdf"},
    }
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()
    mock_session.get.return_value = mock_response
    mock_session_class.return_value = mock_session

    api = OpenAlexAPI()
    result = api.get_paper_details("123")

    assert result is not None
    assert result["title"] == "Test Paper"
    assert result["paperId"] == "W123"
    assert result["reference_count"] == 2
    assert result["authors"] == ["Author 1"]


@patch("jupyterlab_research_assistant_wwc_copilot.services.openalex.requests.Session")
def test_get_paper_details_not_found(mock_session_class):
    """Test handling of paper not found."""
    mock_session = Mock()
    mock_response = Mock()
    mock_response.status_code = 404
    mock_session.get.return_value = mock_response
    mock_session_class.return_value = mock_session

    api = OpenAlexAPI()
    result = api.get_paper_details("nonexistent")

    assert result is None
