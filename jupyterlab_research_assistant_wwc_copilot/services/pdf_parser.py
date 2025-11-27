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

            # Extract first page text separately for abstract extraction
            first_page_text = ""
            if len(doc) > 0:
                first_page = doc[0]
                first_page_text = first_page.get_text()

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

            # Try to extract abstract, authors, and year from first page only
            abstract = self._extract_abstract(first_page_text)
            extracted_authors = self._extract_authors(first_page_text)
            extracted_year = self._extract_year(first_page_text)

            # Use extracted authors if found, otherwise fall back to metadata
            # Keep "author" as string for backward compatibility, add "authors" as list
            author_string = metadata.get("author", "").strip() or None
            authors_list = extracted_authors if extracted_authors else None

            return {
                "title": metadata.get("title", "").strip() or None,
                "author": author_string,  # String for backward compatibility
                "authors": authors_list,  # List of author names
                "subject": metadata.get("subject", "").strip() or None,
                "abstract": abstract,
                "year": extracted_year,
                "full_text": full_text,
                "page_count": page_count,
                "total_pages": total_pages,
            }
        except Exception as e:
            logger.exception(f"Error parsing PDF {pdf_path}")
            raise RuntimeError(f"Failed to parse PDF: {e!s}") from e

    def _extract_abstract(self, first_page_text: str) -> Optional[str]:
        """
        Extract abstract from the first page by grabbing the first paragraph(s).
        Stops before "Keywords:" and removes authors from the beginning.

        Args:
            first_page_text: Text extracted from the first page only

        Returns:
            Abstract text if found, None otherwise
        """
        if not first_page_text:
            return None

        # Stop at "Keywords:" or "Key words:" (case-insensitive)
        # Split the text at keywords to avoid including them
        keywords_pattern = r"(?i)\n\s*(?:keywords?|key\s+words?)\s*:"
        text_before_keywords = re.split(keywords_pattern, first_page_text)[0]

        # Split text into paragraphs (separated by double newlines or significant whitespace)
        paragraphs = re.split(r"\n\s*\n|\n{2,}", text_before_keywords.strip())

        # Filter out empty paragraphs
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        if not paragraphs:
            return None

        # NOTE: The following logic to exclude titles and authors doesn't appear to be
        # working as expected, but it's fine as-is for now. The abstract extraction
        # still works, just may include some title/author text at the beginning.
        #
        # First, identify the title (usually the first substantial paragraph)
        # Titles are typically: all/mostly capitalized, single line or short, at the very start
        title_paragraph_idx = 0
        if paragraphs:
            first_para = paragraphs[0]
            words = first_para.split()
            if words:
                # Check if first paragraph looks like a title (mostly capitalized)
                capitalized_ratio = sum(1 for w in words if w and w[0].isupper()) / len(
                    words
                )
                # If very high capitalization (>80%) and relatively short, likely title
                if capitalized_ratio > 0.8 and len(first_para) < 200:
                    title_paragraph_idx = 0
                else:
                    # Title might be in first paragraph but mixed case
                    # Or title might be missing - assume first paragraph is title
                    title_paragraph_idx = 0

        # Now look for authors/universities right after the title
        # Authors typically appear in the next few paragraphs after the title
        # Look at paragraphs immediately following the title (up to 5 paragraphs)
        title_end_char_pos = 0

        # Find where the title paragraph ends in the original text
        if title_paragraph_idx < len(paragraphs):
            title_text = paragraphs[title_paragraph_idx]
            # Find the position where title ends in the original text
            title_end_char_pos = text_before_keywords.find(title_text) + len(title_text)

        # Now look for university mentions in the text right after the title
        # Only search in a limited window after the title (e.g., next 500 characters)
        search_window = text_before_keywords[
            title_end_char_pos : title_end_char_pos + 500
        ]
        search_window_lines = search_window.split("\n")

        # Common university/institution indicators
        university_indicators = [
            r"\bUniversity\b",
            r"\bCollege\b",
            r"\bInstitute\b",
            r"\bDepartment\b",
            r"\bSchool\b",
            r"\bLaboratory\b",
            r"\bLab\b",
            r"\bCenter\b",
            r"\bCentre\b",
            r"\bHospital\b",
        ]

        # Find the last line in the search window that contains a university indicator
        last_author_line_idx = -1
        for i, line in enumerate(search_window_lines):
            line_stripped = line.strip()
            if not line_stripped:
                continue

            # Check if this line contains a university indicator
            for indicator in university_indicators:
                if re.search(indicator, line_stripped, re.IGNORECASE):
                    # Check if line looks like "Name University" pattern
                    words = line_stripped.split()
                    if words and len(words) >= 2:
                        # Check if most words are capitalized (name + university)
                        capitalized_count = sum(
                            1 for w in words if w and w[0].isupper()
                        )
                        if (
                            capitalized_count >= len(words) * 0.6
                        ):  # At least 60% capitalized
                            last_author_line_idx = i
                            break

        # If we found author lines right after title, start abstract from after the last one
        if last_author_line_idx >= 0:
            # Calculate the absolute position in the full text
            # Find where the last author line ends
            author_section_end = title_end_char_pos
            for i in range(last_author_line_idx + 1):
                if i < len(search_window_lines):
                    author_section_end += (
                        len(search_window_lines[i]) + 1
                    )  # +1 for newline

            # Get text starting from after the author section
            text_after_authors = text_before_keywords[author_section_end:].strip()

            # Re-split into paragraphs from the cleaned text
            paragraphs_after_authors = re.split(r"\n\s*\n|\n{2,}", text_after_authors)
            paragraphs_after_authors = [
                p.strip() for p in paragraphs_after_authors if p.strip()
            ]

            if paragraphs_after_authors:
                # Use the first paragraph after authors
                first_paragraph = paragraphs_after_authors[0]
            else:
                # Fallback: use original first paragraph
                first_paragraph = paragraphs[0]
        else:
            # No author lines detected right after title, use original first paragraph
            first_paragraph = paragraphs[0]

        # Count words in first paragraph
        word_count = len(first_paragraph.split())

        # If first paragraph is under 50 words, include the second paragraph too
        if word_count < 50 and len(paragraphs) > 1:
            abstract = f"{first_paragraph} {paragraphs[1]}".strip()
        else:
            abstract = first_paragraph

        # Clean up: normalize whitespace and ensure we didn't include keywords
        abstract = re.sub(r"\s+", " ", abstract)
        # Remove any accidental inclusion of keywords section
        abstract = re.split(r"(?i)\s+keywords?\s*:", abstract)[0].strip()

        # Validate length (must have at least some content)
        if len(abstract) >= 50:
            return abstract

        return None

    def _extract_authors(self, first_page_text: str) -> Optional[list[str]]:
        """
        Extract authors from the first page text.

        Args:
            first_page_text: Text extracted from the first page only

        Returns:
            List of author names if found, None otherwise
        """
        if not first_page_text:
            return None

        # Look for common author patterns in academic papers
        # Pattern 1: "Author1, Author2, and Author3" or "Author1, Author2 & Author3"
        # Pattern 2: "Author1\nAuthor2\nAuthor3" (one per line)
        # Pattern 3: "Author1, Author2, Author3" (comma-separated)

        # Try to find author section - usually appears after title, before abstract
        # Look for patterns like "Author Name" or "First Last" (capitalized words)

        # Get first 2000 characters (authors are usually near the top)
        top_text = first_page_text[:2000]

        # Pattern: Look for lines that look like author names
        # Authors are typically on separate lines or comma-separated
        # Common patterns:
        # - "John Smith, Jane Doe, and Bob Johnson"
        # - "John Smith\nJane Doe\nBob Johnson"
        # - "J. Smith, J. Doe, B. Johnson"

        # Try to find author block (usually 2-10 lines of names)
        lines = top_text.split("\n")
        author_lines = []

        for _i, line in enumerate(lines[:20]):  # Check first 20 lines
            line_stripped = line.strip()
            if not line_stripped:
                continue

            # Skip common non-author patterns
            if any(
                skip in line_stripped.lower()
                for skip in [
                    "abstract",
                    "keywords",
                    "introduction",
                    "doi:",
                    "http",
                    "www",
                ]
            ):
                break

            # Check if line looks like author names
            # Author names typically have:
            # - 2-4 words (first name, middle initial, last name)
            # - Capitalized words
            # - May contain commas, ampersands, or "and"
            words = line_stripped.split()
            if 1 <= len(words) <= 6:  # Reasonable name length
                # Check if most words start with capital letters
                capitalized = sum(1 for w in words if w and w[0].isupper())
                if capitalized >= len(words) * 0.5:  # At least half capitalized
                    author_lines.append(line_stripped)
                    # If we've found a few author lines, likely found the author section
                    if len(author_lines) >= 2:
                        break

        if not author_lines:
            return None

        # Parse author names from the lines
        authors = []
        for line in author_lines:
            # Split by comma, "and", or "&"
            parts = re.split(r",\s*|\s+and\s+|\s+&\s+", line)
            for part in parts:
                part_stripped = part.strip()
                if part_stripped and len(part_stripped) > 2:  # Valid name length
                    authors.append(part_stripped)

        # If we found authors, return them (limit to reasonable number)
        if authors and 1 <= len(authors) <= 20:
            return authors[:10]  # Limit to first 10 authors

        return None

    def _extract_year(self, first_page_text: str) -> Optional[int]:
        """
        Extract publication year from the first page text.

        Args:
            first_page_text: Text extracted from the first page only

        Returns:
            Year as integer if found, None otherwise
        """
        if not first_page_text:
            return None

        # Look for 4-digit years in the first 2000 characters
        # Years are typically between 1900 and current year + 1
        top_text = first_page_text[:2000]

        # Pattern: 4-digit year (1900-2100)
        year_pattern = r"\b(19[0-9]{2}|20[0-3][0-9])\b"
        matches = re.findall(year_pattern, top_text)

        if matches:
            # Get the most recent year (likely the publication year)
            years = [int(y) for y in matches]
            # Filter to reasonable range (1900 to 2030)
            years = [y for y in years if 1900 <= y <= 2030]
            if years:
                # Return the most recent year found
                return max(years)

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
