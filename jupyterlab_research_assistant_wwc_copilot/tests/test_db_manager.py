"""Tests for database manager."""

import pytest
import os
from jupyterlab_research_assistant_wwc_copilot.services.db_manager import (
    DatabaseManager
)
from jupyterlab_research_assistant_wwc_copilot.database.models import (
    create_db_engine,
    Base
)


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    """Create a temporary database for testing."""
    # Override the database path to use a temporary file
    test_db_path = tmp_path / "test_research_library.db"

    def mock_get_db_path():
        return test_db_path
    
    monkeypatch.setattr(
        "jupyterlab_research_assistant_wwc_copilot.database.models.get_db_path",
        mock_get_db_path
    )
    
    # Create the database
    engine = create_db_engine()
    Base.metadata.create_all(engine)
    engine.dispose()
    
    yield test_db_path
    
    # Cleanup
    if test_db_path.exists():
        os.remove(test_db_path)


def test_add_paper(temp_db):
    """Test adding a paper to the database."""
    with DatabaseManager() as db:
        paper_data = {
            "title": "Test Paper",
            "authors": ["John Doe", "Jane Smith"],
            "year": 2023,
            "abstract": "This is a test abstract"
        }
        result = db.add_paper(paper_data)
        assert result["id"] is not None
        assert result["title"] == "Test Paper"
        assert result["authors"] == ["John Doe", "Jane Smith"]
        assert result["year"] == 2023


def test_get_all_papers(temp_db):
    """Test retrieving all papers."""
    with DatabaseManager() as db:
        # Add a paper
        db.add_paper({
            "title": "Paper 1",
            "authors": ["Author 1"],
            "year": 2023
        })
        db.add_paper({
            "title": "Paper 2",
            "authors": ["Author 2"],
            "year": 2024
        })

    with DatabaseManager() as db:
        papers = db.get_all_papers()
        assert len(papers) == 2
        assert papers[0]["title"] in ["Paper 1", "Paper 2"]
        assert papers[1]["title"] in ["Paper 1", "Paper 2"]


def test_get_paper_by_id(temp_db):
    """Test retrieving a paper by ID."""
    with DatabaseManager() as db:
        paper = db.add_paper({
            "title": "Test Paper",
            "authors": ["Author"],
            "year": 2023
        })
        paper_id = paper["id"]

    with DatabaseManager() as db:
        retrieved = db.get_paper_by_id(paper_id)
        assert retrieved is not None
        assert retrieved["title"] == "Test Paper"
        assert retrieved["id"] == paper_id


def test_search_papers(temp_db):
    """Test searching papers."""
    with DatabaseManager() as db:
        db.add_paper({
            "title": "Spaced Repetition Study",
            "authors": ["Researcher"],
            "abstract": "This paper studies spaced repetition",
            "year": 2023
        })
        db.add_paper({
            "title": "Different Topic",
            "authors": ["Another Researcher"],
            "abstract": "This is about something else",
            "year": 2024
        })

    with DatabaseManager() as db:
        results = db.search_papers("spaced repetition")
        assert len(results) == 1
        assert "Spaced Repetition" in results[0]["title"]


def test_add_paper_with_metadata(temp_db):
    """Test adding a paper with study and learning science metadata."""
    with DatabaseManager() as db:
        paper_data = {
            "title": "Test Paper",
            "authors": ["Author"],
            "year": 2023,
            "study_metadata": {
                "methodology": "RCT",
                "sample_size_baseline": 100,
                "sample_size_endline": 95,
                "effect_sizes": {
                    "outcome1": {"d": 0.5, "se": 0.1}
                }
            },
            "learning_science_metadata": {
                "learning_domain": "cognitive",
                "intervention_type": "Spaced Repetition"
            }
        }
        result = db.add_paper(paper_data)
        assert result["study_metadata"]["methodology"] == "RCT"
        assert result["learning_science_metadata"]["learning_domain"] == "cognitive"

