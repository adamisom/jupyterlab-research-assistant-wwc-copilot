"""
PDF text and metadata extraction using PyMuPDF.

IMPORTANT FOR DEVELOPERS:
- PyMuPDF (fitz) is imported as 'fitz' for historical compatibility
- Safety limits prevent memory exhaustion with very large PDFs
- Always close documents to free memory (handled in try/finally or context manager)
"""

import logging
import re
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF (imported as 'fitz' for historical reasons)

logger = logging.getLogger(__name__)


class PDFParser:
    """Parser for extracting text and metadata from PDF files."""

    # CRITICAL: Safety limits to prevent memory exhaustion
    # Very large PDFs (e.g., 1000+ pages) can consume excessive memory
    MAX_PAGES = 200  # Safety limit for very large PDFs
    MAX_TEXT_LENGTH = 500000  # ~500KB of text (prevents memory issues)

    def extract_text_and_metadata(self, pdf_path: str) -> dict:
        """
        Extract full text and metadata from a PDF file.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with 'title', 'author', 'subject', 'abstract', 'full_text', 'page_count'

        Raises:
            FileNotFoundError: If PDF doesn't exist
            Exception: If PDF is corrupted or unreadable
        """
        pdf_path_obj = Path(pdf_path)
        if not pdf_path_obj.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        try:
            # CRITICAL: Always close document to free memory
            # PyMuPDF keeps document in memory until explicitly closed
            doc = fitz.open(str(pdf_path_obj))

            # Extract metadata from PDF properties (title, author, subject)
            metadata = doc.metadata

            # Extract full text (with page limit for safety)
            # NOTE: get_text() extracts plain text - formatting/layout info is lost
            full_text = ""
            total_pages = len(doc)
            page_count = min(total_pages, self.MAX_PAGES)

            for page_num in range(page_count):
                page = doc[page_num]
                page_text = page.get_text()
                full_text += page_text + "\n"

                # Safety check for extremely long documents
                # Prevents memory exhaustion with text-heavy PDFs
                if len(full_text) > self.MAX_TEXT_LENGTH:
                    logger.warning(
                        f"PDF text truncated at {self.MAX_TEXT_LENGTH} characters"
                    )
                    break

            doc.close()  # CRITICAL: Free memory

            # Try to extract abstract from full_text
            abstract = self._extract_abstract(full_text)

            return {
                "title": metadata.get("title", "").strip() or None,
                "author": metadata.get("author", "").strip() or None,
                "subject": metadata.get("subject", "").strip() or None,
                "abstract": abstract,
                "full_text": full_text,
                "page_count": page_count,
                "total_pages": total_pages,
            }
        except Exception as e:
            logger.exception(f"Error parsing PDF {pdf_path}")
            raise RuntimeError(f"Failed to parse PDF: {e!s}") from e

    def _extract_abstract(self, full_text: str) -> Optional[str]:
        """
        Extract abstract from PDF text by looking for common patterns.

        Args:
            full_text: Full text extracted from PDF

        Returns:
            Abstract text if found, None otherwise
        """
        if not full_text:
            return None

        # Common patterns for abstract sections
        # Look for "Abstract" heading followed by text, ending before "Keywords", "Introduction", etc.
        # Pattern 1: "Abstract" (case-insensitive) followed by optional punctuation/whitespace
        # Capture text until "Keywords", "Key words", "Introduction", or end of reasonable abstract length
        patterns = [
            r"(?i)\babstract\b[:\s]*\n?\s*(.+?)(?=\n\s*(?:keywords?|introduction|background|method|1\.|i\.|§))",
            r"(?i)\babstract\b[:\s]*\n?\s*(.{100,2000})",  # Fallback: 100-2000 chars after "Abstract"
        ]

        for pattern in patterns:
            match = re.search(pattern, full_text, re.DOTALL | re.MULTILINE)
            if match:
                abstract = match.group(1).strip()
                # Clean up: remove extra whitespace, newlines
                abstract = re.sub(r"\s+", " ", abstract)
                # Limit length (abstracts are typically 100-500 words, ~500-3000 chars)
                if 50 <= len(abstract) <= 3000:
                    return abstract

        return None

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
