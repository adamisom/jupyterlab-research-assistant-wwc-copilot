"""PDF text and metadata extraction using PyMuPDF."""

import fitz  # PyMuPDF
from typing import Dict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PDFParser:
    """Parser for extracting text and metadata from PDF files."""

    MAX_PAGES = 200  # Safety limit for very large PDFs
    MAX_TEXT_LENGTH = 500000  # ~500KB of text

    def extract_text_and_metadata(self, pdf_path: str) -> Dict:
        """
        Extract full text and metadata from a PDF file.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with 'title', 'author', 'subject', 'full_text', 'page_count'

        Raises:
            FileNotFoundError: If PDF doesn't exist
            Exception: If PDF is corrupted or unreadable
        """
        pdf_path_obj = Path(pdf_path)
        if not pdf_path_obj.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        try:
            doc = fitz.open(str(pdf_path_obj))

            # Extract metadata from PDF properties
            metadata = doc.metadata

            # Extract full text (with page limit for safety)
            full_text = ""
            total_pages = len(doc)
            page_count = min(total_pages, self.MAX_PAGES)

            for page_num in range(page_count):
                page = doc[page_num]
                page_text = page.get_text()
                full_text += page_text + "\n"

                # Safety check for extremely long documents
                if len(full_text) > self.MAX_TEXT_LENGTH:
                    logger.warning(
                        f"PDF text truncated at {self.MAX_TEXT_LENGTH} characters"
                    )
                    break

            doc.close()

            return {
                "title": metadata.get("title", "").strip() or None,
                "author": metadata.get("author", "").strip() or None,
                "subject": metadata.get("subject", "").strip() or None,
                "full_text": full_text,
                "page_count": page_count,
                "total_pages": total_pages
            }
        except Exception as e:
            logger.error(f"Error parsing PDF {pdf_path}: {str(e)}")
            raise Exception(f"Failed to parse PDF: {str(e)}") from e

    def extract_text_chunk(self, pdf_path: str, max_chars: int = 16000) -> str:
        """
        Extract a chunk of text from the beginning of a PDF (for AI processing).

        Args:
            pdf_path: Path to PDF file
            max_chars: Maximum characters to extract

        Returns:
            Text chunk (first max_chars characters)
        """
        result = self.extract_text_and_metadata(pdf_path)
        text = result["full_text"]
        return text[:max_chars] if len(text) > max_chars else text


