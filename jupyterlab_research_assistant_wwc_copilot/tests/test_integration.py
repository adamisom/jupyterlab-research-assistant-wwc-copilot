"""Integration tests for full workflow."""

import pytest
import os
from unittest.mock import Mock, patch
from pathlib import Path
from jupyterlab_research_assistant_wwc_copilot.services.db_manager import DatabaseManager
from jupyterlab_research_assistant_wwc_copilot.services.semantic_scholar import SemanticScholarAPI
from jupyterlab_research_assistant_wwc_copilot.database.models import (
    Paper,
    StudyMetadata,
    LearningScienceMetadata,
    create_db_engine,
    Base,
    get_db_path
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


@pytest.fixture
def db(temp_db):
    """Create a database manager with temporary database."""
    with DatabaseManager() as db:
        yield db
        # Cleanup: delete all test papers and related metadata
        try:
            # Delete related metadata first (foreign key constraints)
            test_papers = db.session.query(Paper).filter(Paper.title.like("TEST_%")).all()
            for paper in test_papers:
                db.session.query(StudyMetadata).filter_by(paper_id=paper.id).delete()
                db.session.query(LearningScienceMetadata).filter_by(paper_id=paper.id).delete()
            # Then delete papers
            db.session.query(Paper).filter(Paper.title.like("TEST_%")).delete()
            db.session.commit()
        except Exception:
            db.session.rollback()


@patch("jupyterlab_research_assistant_wwc_copilot.services.semantic_scholar.requests.Session")
def test_complete_workflow(mock_session_class, db):
    """Test: Search → Import → View → Search → Export"""
    # Mock Semantic Scholar API
    mock_session = Mock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "data": [{
            "paperId": "123",
            "title": "Test Paper on Spaced Repetition",
            "authors": [{"name": "Test Author"}],
            "year": 2023,
            "abstract": "This is a test abstract about spaced repetition",
            "doi": "10.1234/test",
            "citationCount": 10
        }],
        "total": 1
    }
    mock_response.raise_for_status = Mock()
    mock_session.get.return_value = mock_response
    mock_session_class.return_value = mock_session

    # 1. Search Semantic Scholar
    api = SemanticScholarAPI()
    results = api.search_papers("spaced repetition", limit=1)
    assert len(results["data"]) > 0

    # 2. Import paper
    paper_data = results["data"][0]
    imported = db.add_paper({
        "title": f"TEST_{paper_data['title']}",
        "authors": paper_data.get("authors", []),
        "year": paper_data.get("year"),
        "abstract": paper_data.get("abstract", "")
    })
    assert imported["id"] is not None

    # 3. View in library
    papers = db.get_all_papers()
    assert any(p["id"] == imported["id"] for p in papers)

    # 4. Search library
    search_results = db.search_papers("spaced")
    assert len(search_results) > 0

    # 5. Get paper details
    paper = db.get_paper_by_id(imported["id"])
    assert paper is not None
    assert paper["title"].startswith("TEST_")


def test_error_handling(db):
    """Test error scenarios."""
    # Test search with empty query
    results = db.search_papers("")
    assert isinstance(results, list)

    # Test getting non-existent paper
    paper = db.get_paper_by_id(99999)
    assert paper is None


@patch("jupyterlab_research_assistant_wwc_copilot.services.semantic_scholar.requests.Session")
@pytest.mark.parametrize("query", [
    "spaced repetition",
    "learning science",
    "meta-analysis",
    "RCT education"
])
def test_search_variations(mock_session_class, query, db):
    """Test various search queries."""
    # Mock Semantic Scholar API
    mock_session = Mock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "data": [{
            "paperId": "123",
            "title": f"Test Paper on {query}",
            "authors": [{"name": "Test Author"}],
            "year": 2023,
            "abstract": f"Test abstract about {query}",
            "citationCount": 5
        }],
        "total": 1
    }
    mock_response.raise_for_status = Mock()
    mock_session.get.return_value = mock_response
    mock_session_class.return_value = mock_session

    api = SemanticScholarAPI()
    results = api.search_papers(query, limit=5)
    assert "data" in results
    assert "total" in results


def test_paper_with_metadata(db):
    """Test adding paper with study and learning science metadata."""
    paper_data = {
        "title": "TEST_Paper with Metadata",
        "authors": ["Test Author"],
        "year": 2023,
        "abstract": "Test abstract",
        "study_metadata": {
            "methodology": "RCT",
            "sample_size_baseline": 100,
            "sample_size_endline": 95,
            "effect_sizes": {
                "test_score": {"d": 0.5, "se": 0.1}
            }
        },
        "learning_science_metadata": {
            "learning_domain": "cognitive",
            "intervention_type": "Spaced Repetition"
        }
    }

    imported = db.add_paper(paper_data)
    assert imported["id"] is not None
    assert imported["study_metadata"]["methodology"] == "RCT"
    assert imported["learning_science_metadata"]["learning_domain"] == "cognitive"

    # Retrieve and verify
    retrieved = db.get_paper_by_id(imported["id"])
    assert retrieved is not None
    assert retrieved["study_metadata"]["methodology"] == "RCT"
    assert retrieved["learning_science_metadata"]["learning_domain"] == "cognitive"

