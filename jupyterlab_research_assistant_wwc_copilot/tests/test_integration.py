"""Integration tests for full workflow."""

import pytest
from pathlib import Path
from jupyterlab_research_assistant_wwc_copilot.services.db_manager import DatabaseManager
from jupyterlab_research_assistant_wwc_copilot.services.semantic_scholar import SemanticScholarAPI
from jupyterlab_research_assistant_wwc_copilot.database.models import Paper


@pytest.fixture
def db():
    """Create a test database."""
    with DatabaseManager() as db:
        yield db
        # Cleanup: delete all test papers
        try:
            db.session.query(Paper).filter(Paper.title.like("TEST_%")).delete()
            db.session.commit()
        except Exception:
            db.session.rollback()


def test_complete_workflow(db):
    """Test: Search → Import → View → Search → Export"""
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


@pytest.mark.parametrize("query", [
    "spaced repetition",
    "learning science",
    "meta-analysis",
    "RCT education"
])
def test_search_variations(query, db):
    """Test various search queries."""
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

