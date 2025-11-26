"""Tests for import service."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from jupyterlab_research_assistant_wwc_copilot.services.ai_extractor import AIExtractor
from jupyterlab_research_assistant_wwc_copilot.services.import_service import (
    ImportService,
)
from jupyterlab_research_assistant_wwc_copilot.services.pdf_parser import PDFParser


@pytest.fixture
def mock_pdf_parser():
    """Create a mock PDF parser."""
    parser = Mock(spec=PDFParser)
    parser.extract_text_and_metadata.return_value = {
        "title": "Test PDF Title",
        "author": "Test Author",
        "full_text": "Full text content",
        "page_count": 10,
    }
    return parser


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    """Create a temporary database for testing."""
    import os

    from jupyterlab_research_assistant_wwc_copilot.database.models import (
        Base,
        create_db_engine,
    )

    test_db_path = tmp_path / "test_research_library.db"

    def mock_get_db_path():
        return test_db_path

    monkeypatch.setattr(
        "jupyterlab_research_assistant_wwc_copilot.database.models.get_db_path",
        mock_get_db_path,
    )

    engine = create_db_engine()
    Base.metadata.create_all(engine)
    engine.dispose()

    yield test_db_path

    if test_db_path.exists():
        os.remove(test_db_path)


@patch("jupyterlab_research_assistant_wwc_copilot.services.import_service.Path")
def test_import_pdf_basic(mock_path_class, mock_pdf_parser, temp_db):
    """Test basic PDF import without AI extraction."""
    # Mock file path operations
    mock_upload_dir = MagicMock()
    mock_file_path = MagicMock()
    mock_file_path.__str__ = lambda x: "/tmp/test.pdf"
    mock_upload_dir.__truediv__ = lambda x, y: mock_file_path
    mock_upload_dir.mkdir = Mock()
    mock_path_class.home.return_value.__truediv__.return_value = mock_upload_dir

    service = ImportService(pdf_parser=mock_pdf_parser, ai_extractor=None)

    file_content = b"fake pdf content"
    filename = "test.pdf"

    result = service.import_pdf(
        file_content=file_content, filename=filename, ai_config=None
    )

    assert result is not None
    assert "paper" in result
    assert "title" in result["paper"]
    # Verify PDF parser was called
    mock_pdf_parser.extract_text_and_metadata.assert_called_once()


@patch("jupyterlab_research_assistant_wwc_copilot.services.import_service.Path")
def test_import_pdf_with_ai_extraction(mock_path_class, mock_pdf_parser, temp_db):
    """Test PDF import with AI extraction enabled."""
    mock_upload_dir = MagicMock()
    mock_file_path = MagicMock()
    mock_file_path.__str__ = lambda x: "/tmp/test.pdf"
    mock_upload_dir.__truediv__ = lambda x, y: mock_file_path
    mock_upload_dir.mkdir = Mock()
    mock_path_class.home.return_value.__truediv__.return_value = mock_upload_dir

    mock_ai_extractor = Mock(spec=AIExtractor)
    mock_ai_extractor.extract_metadata.return_value = {
        "study_metadata": {"methodology": "RCT", "sample_size_baseline": 100},
        "learning_science_metadata": {"learning_domain": "cognitive"},
    }

    service = ImportService(pdf_parser=mock_pdf_parser, ai_extractor=mock_ai_extractor)

    file_content = b"fake pdf content"
    filename = "test.pdf"
    ai_config = {"enabled": True, "provider": "ollama"}

    result = service.import_pdf(
        file_content=file_content, filename=filename, ai_config=ai_config
    )

    assert result is not None
    # Verify AI extractor was called
    mock_ai_extractor.extract_metadata.assert_called_once()


@patch("jupyterlab_research_assistant_wwc_copilot.services.import_service.Path")
def test_import_pdf_ai_extraction_failure_continues(
    mock_path_class, mock_pdf_parser, temp_db
):
    """Test that AI extraction failure doesn't fail the import."""

    mock_upload_dir = MagicMock()
    mock_file_path = MagicMock()
    mock_file_path.__str__ = lambda x: "/tmp/test.pdf"
    mock_upload_dir.__truediv__ = lambda x, y: mock_file_path
    mock_upload_dir.mkdir = Mock()
    mock_path_class.home.return_value.__truediv__.return_value = mock_upload_dir

    mock_ai_extractor = Mock(spec=AIExtractor)
    mock_ai_extractor.extract_metadata.side_effect = Exception("AI extraction failed")

    service = ImportService(pdf_parser=mock_pdf_parser, ai_extractor=mock_ai_extractor)

    file_content = b"fake pdf content"
    filename = "test.pdf"
    ai_config = {"enabled": True, "provider": "ollama"}

    # Should not raise exception
    result = service.import_pdf(
        file_content=file_content, filename=filename, ai_config=ai_config
    )

    assert result is not None
    # Import should succeed even if AI extraction fails


@patch("jupyterlab_research_assistant_wwc_copilot.services.import_service.Path")
def test_import_pdf_duplicate_with_full_pdf(mock_path_class, mock_pdf_parser, temp_db):
    """Test PDF import when existing paper already has full PDF."""
    from jupyterlab_research_assistant_wwc_copilot.services.db_manager import (
        DatabaseManager,
    )

    # First, add a paper with full PDF to the database
    with DatabaseManager() as db:
        existing_paper = db.add_paper(
            {
                "title": "Test PDF Title",
                "authors": ["Test Author"],
                "year": 2023,
                "pdf_path": "/tmp/existing.pdf",
                "full_text": "Existing full text",
            }
        )

    # Mock file path operations
    mock_upload_dir = MagicMock()
    mock_file_path = MagicMock()
    mock_file_path.__str__ = lambda x: "/tmp/test.pdf"
    mock_upload_dir.__truediv__ = lambda x, y: mock_file_path
    mock_upload_dir.mkdir = Mock()
    mock_path_class.home.return_value.__truediv__.return_value = mock_upload_dir

    service = ImportService(pdf_parser=mock_pdf_parser, ai_extractor=None)

    file_content = b"fake pdf content"
    filename = "test.pdf"

    result = service.import_pdf(
        file_content=file_content, filename=filename, ai_config=None
    )

    # Should return existing paper with duplicate flags
    assert result is not None
    assert result["is_duplicate"] is True
    assert result["already_has_pdf"] is True
    assert result["paper"]["id"] == existing_paper["id"]
    assert result["paper"]["pdf_path"] == "/tmp/existing.pdf"
    # PDF parser should not be called since we're not uploading
    mock_pdf_parser.extract_text_and_metadata.assert_called_once()


@patch("jupyterlab_research_assistant_wwc_copilot.services.import_service.Path")
def test_import_pdf_duplicate_metadata_only(mock_path_class, mock_pdf_parser, temp_db):
    """Test PDF import when existing paper is metadata-only."""
    from jupyterlab_research_assistant_wwc_copilot.services.db_manager import (
        DatabaseManager,
    )

    # First, add a metadata-only paper to the database
    with DatabaseManager() as db:
        existing_paper = db.add_paper(
            {
                "title": "Test PDF Title",
                "authors": ["Test Author"],
                "year": 2023,
                "abstract": "Test abstract",
                # No pdf_path or full_text
            }
        )

    # Mock file path operations
    mock_upload_dir = MagicMock()
    mock_file_path = MagicMock()
    mock_file_path.__str__ = lambda x: "/tmp/new.pdf"
    mock_upload_dir.__truediv__ = lambda x, y: mock_file_path
    mock_upload_dir.mkdir = Mock()
    mock_path_class.home.return_value.__truediv__.return_value = mock_upload_dir

    service = ImportService(pdf_parser=mock_pdf_parser, ai_extractor=None)

    file_content = b"fake pdf content"
    filename = "test.pdf"

    result = service.import_pdf(
        file_content=file_content, filename=filename, ai_config=None
    )

    # Should update existing paper with PDF data
    assert result is not None
    assert result["is_duplicate"] is True
    assert result["already_has_pdf"] is False
    assert result["paper"]["id"] == existing_paper["id"]
    # Should now have PDF data
    assert result["paper"]["pdf_path"] is not None
    assert result["paper"]["full_text"] == "Full text content"
    # Should preserve existing abstract
    assert result["paper"]["abstract"] == "Test abstract"


@patch("jupyterlab_research_assistant_wwc_copilot.services.import_service.Path")
def test_import_pdf_new_paper(mock_path_class, mock_pdf_parser, temp_db):
    """Test PDF import for a new paper (no duplicate)."""
    # Mock file path operations
    mock_upload_dir = MagicMock()
    mock_file_path = MagicMock()
    mock_file_path.__str__ = lambda x: "/tmp/test.pdf"
    mock_upload_dir.__truediv__ = lambda x, y: mock_file_path
    mock_upload_dir.mkdir = Mock()
    mock_path_class.home.return_value.__truediv__.return_value = mock_upload_dir

    service = ImportService(pdf_parser=mock_pdf_parser, ai_extractor=None)

    file_content = b"fake pdf content"
    filename = "new_paper.pdf"

    result = service.import_pdf(
        file_content=file_content, filename=filename, ai_config=None
    )

    # Should add new paper
    assert result is not None
    assert result["is_duplicate"] is False
    assert "already_has_pdf" not in result or result.get("already_has_pdf") is False
    assert result["paper"]["title"] == "Test PDF Title"
