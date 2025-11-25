"""Tests for export formatter service."""

import pytest
from jupyterlab_research_assistant_wwc_copilot.services.export_formatter import (
    ExportFormatter
)


def test_to_json():
    """Test JSON export formatting."""
    papers = [
        {
            "id": 1,
            "title": "Test Paper",
            "authors": ["Author 1", "Author 2"],
            "year": 2023,
            "doi": "10.1234/test",
            "citation_count": 10,
            "abstract": "Test abstract"
        }
    ]

    result = ExportFormatter.to_json(papers)
    assert isinstance(result, str)
    assert "Test Paper" in result
    assert "2023" in result


def test_to_csv():
    """Test CSV export formatting."""
    papers = [
        {
            "id": 1,
            "title": "Test Paper",
            "authors": ["Author 1", "Author 2"],
            "year": 2023,
            "doi": "10.1234/test",
            "citation_count": 10,
            "abstract": "Test abstract"
        }
    ]

    result = ExportFormatter.to_csv(papers)
    assert isinstance(result, str)
    assert "Test Paper" in result
    assert "Author 1, Author 2" in result
    assert "2023" in result
    # Check CSV header
    assert "id,title,authors,year,doi,citation_count,abstract" in result


def test_to_bibtex():
    """Test BibTeX export formatting."""
    papers = [
        {
            "id": 1,
            "title": "Test Paper",
            "authors": ["John Doe", "Jane Smith"],
            "year": 2023,
            "doi": "10.1234/test",
            "abstract": "Test abstract"
        }
    ]

    result = ExportFormatter.to_bibtex(papers)
    assert isinstance(result, str)
    assert "@article" in result
    assert "Test Paper" in result
    assert "doe2023" in result.lower()  # Citation key
    assert "John Doe and Jane Smith" in result
    assert "2023" in result


def test_to_bibtex_no_authors():
    """Test BibTeX export with no authors."""
    papers = [
        {
            "id": 1,
            "title": "Test Paper",
            "authors": [],
            "year": 2023
        }
    ]

    result = ExportFormatter.to_bibtex(papers)
    assert "unknown2023" in result.lower()


def test_to_bibtex_escapes_special_chars():
    """Test BibTeX export escapes special characters in abstract."""
    papers = [
        {
            "id": 1,
            "title": "Test Paper",
            "authors": ["Author"],
            "year": 2023,
            "abstract": "Abstract with {braces} and } more {"
        }
    ]

    result = ExportFormatter.to_bibtex(papers)
    assert "\\{" in result
    assert "\\}" in result

