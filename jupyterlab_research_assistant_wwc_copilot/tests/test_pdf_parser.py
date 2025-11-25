"""Tests for PDF parser."""

from typing import Optional
import pytest
from jupyterlab_research_assistant_wwc_copilot.services.pdf_parser import PDFParser


def test_pdf_parser_file_not_found():
    """Test that FileNotFoundError is raised for non-existent files."""
    parser = PDFParser()
    with pytest.raises(FileNotFoundError):
        parser.extract_text_and_metadata("/nonexistent/file.pdf")


def test_extract_text_chunk_empty_file(tmp_path):
    """Test extracting text chunk from a non-existent file."""
    parser = PDFParser()
    with pytest.raises(FileNotFoundError):
        parser.extract_text_chunk(str(tmp_path / "nonexistent.pdf"))


# Note: Testing with actual PDFs would require sample PDF files
# For now, we test error cases and structure
# Integration tests with real PDFs should be added separately

