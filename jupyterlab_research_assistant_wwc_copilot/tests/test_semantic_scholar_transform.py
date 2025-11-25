"""Tests for Semantic Scholar API paper transformation."""

import pytest
from jupyterlab_research_assistant_wwc_copilot.services.semantic_scholar import (
    SemanticScholarAPI
)


def test_transform_paper_basic():
    """Test basic paper transformation."""
    api = SemanticScholarAPI()
    paper = {
        "paperId": "123",
        "title": "Test Paper",
        "authors": [{"name": "Author 1"}, {"name": "Author 2"}],
        "year": 2023,
        "abstract": "Test abstract",
        "doi": "10.1234/test",
        "citationCount": 10,
        "openAccessPdf": None
    }

    result = api._transform_paper(paper)

    assert result["paperId"] == "123"
    assert result["title"] == "Test Paper"
    assert result["authors"] == ["Author 1", "Author 2"]
    assert result["year"] == 2023
    assert result["citation_count"] == 10
    assert result["open_access_pdf"] is None


def test_transform_paper_with_open_access_pdf():
    """Test paper transformation with open access PDF."""
    api = SemanticScholarAPI()
    paper = {
        "paperId": "123",
        "title": "Test Paper",
        "authors": [],
        "year": 2023,
        "openAccessPdf": {"url": "https://example.com/paper.pdf"}
    }

    result = api._transform_paper(paper)

    assert result["open_access_pdf"] == "https://example.com/paper.pdf"


def test_transform_paper_with_references():
    """Test paper transformation with reference count."""
    api = SemanticScholarAPI()
    paper = {
        "paperId": "123",
        "title": "Test Paper",
        "authors": [],
        "year": 2023,
        "citationCount": 10,
        "referenceCount": 5
    }

    result = api._transform_paper(paper, include_references=True)

    assert result["reference_count"] == 5
    assert "reference_count" in result


def test_transform_paper_without_references():
    """Test paper transformation without reference count."""
    api = SemanticScholarAPI()
    paper = {
        "paperId": "123",
        "title": "Test Paper",
        "authors": [],
        "year": 2023,
        "citationCount": 10,
        "referenceCount": 5
    }

    result = api._transform_paper(paper, include_references=False)

    assert "reference_count" not in result

