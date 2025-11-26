"""Service for importing PDF files and extracting metadata."""

import logging
from pathlib import Path
from typing import Optional

from .ai_extractor import AIExtractor
from .db_manager import DatabaseManager
from .pdf_parser import PDFParser

logger = logging.getLogger(__name__)


class ImportService:
    """Service for orchestrating PDF import workflow."""

    def __init__(
        self, pdf_parser: PDFParser, ai_extractor: Optional[AIExtractor] = None
    ):
        """
        Initialize the import service.

        Args:
            pdf_parser: PDF parser instance
            ai_extractor: Optional AI extractor instance
        """
        self.pdf_parser = pdf_parser
        self.ai_extractor = ai_extractor

    def import_pdf(
        self, file_content: bytes, filename: str, ai_config: Optional[dict] = None
    ) -> dict:
        """
        Import a PDF file and extract metadata.

        Args:
            file_content: PDF file content as bytes
            filename: Original filename
            ai_config: Optional AI extraction configuration

        Returns:
            Dictionary with imported paper data

        Raises:
            Exception: If import fails
        """
        # Save file to temporary location
        upload_dir = Path.home() / ".jupyter" / "research_assistant" / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_path = upload_dir / filename
        with file_path.open("wb") as f:
            f.write(file_content)

        # Extract text and metadata from PDF
        extracted = self.pdf_parser.extract_text_and_metadata(str(file_path))

        # Get title and authors for deduplication check
        title = extracted.get("title") or filename.replace(".pdf", "")
        author = extracted.get("author")
        # Convert author string to list if needed
        # Author might be a comma-separated string, split it
        authors = [a.strip() for a in author.split(",") if a.strip()] if author else []
        # PDF metadata doesn't typically include year, so we'll match without it
        year = None

        # Create paper record
        paper_data = {
            "title": title,
            "authors": authors,
            "year": year,
            "full_text": extracted.get("full_text"),
            "pdf_path": str(file_path),
        }

        # AI extraction (if enabled)
        if ai_config and ai_config.get("enabled"):
            try:
                if not self.ai_extractor:
                    # Create extractor if not provided
                    extractor = AIExtractor(
                        provider=ai_config.get("provider", "ollama"),
                        api_key=ai_config.get("apiKey"),
                        model=ai_config.get("model", "llama3"),
                        ollama_url=ai_config.get("ollamaUrl", "http://localhost:11434"),
                    )
                else:
                    extractor = self.ai_extractor

                ai_metadata = extractor.extract_metadata(extracted.get("full_text", ""))

                # Merge AI-extracted metadata
                if "study_metadata" in ai_metadata:
                    paper_data["study_metadata"] = ai_metadata["study_metadata"]
                if "learning_science_metadata" in ai_metadata:
                    paper_data["learning_science_metadata"] = ai_metadata[
                        "learning_science_metadata"
                    ]
            except Exception as e:
                # Log but don't fail the import if AI extraction fails
                logger.warning(
                    f"AI extraction failed: {e!s}, continuing without AI metadata"
                )

        # Save to database (check for existing paper first)
        with DatabaseManager() as db:
            # Check if paper already exists (same title, authors, year)
            existing_paper = db.find_existing_paper(
                title=title, authors=authors, year=year
            )

            if existing_paper:
                # Check if existing paper already has a full PDF
                has_full_pdf = bool(
                    existing_paper.get("pdf_path") or existing_paper.get("full_text")
                )

                if has_full_pdf:
                    # Paper already has a full PDF - don't upload, just return existing
                    logger.info(
                        f"Found existing paper with full PDF (same title/authors/year): {title}. "
                        f"Not uploading duplicate PDF for paper ID {existing_paper['id']}."
                    )
                    return {
                        "paper": existing_paper,
                        "is_duplicate": True,
                        "already_has_pdf": True,
                    }
                else:
                    # Paper is metadata-only - update it with PDF data
                    logger.info(
                        f"Found existing metadata-only paper (same title/authors/year): {title}. "
                        f"Updating paper ID {existing_paper['id']} with PDF data."
                    )
                    # Merge existing data with new PDF data
                    # Preserve existing metadata that might not be in PDF
                    merged_data = {
                        **existing_paper,  # Keep existing fields
                        **paper_data,  # Overwrite with PDF data (pdf_path, full_text)
                    }
                    # Preserve existing study_metadata and learning_science_metadata
                    # unless AI extraction provides new data
                    if "study_metadata" not in paper_data:
                        merged_data.pop("study_metadata", None)
                    if "learning_science_metadata" not in paper_data:
                        merged_data.pop("learning_science_metadata", None)

                    paper = db.update_paper(existing_paper["id"], merged_data)
                    return {
                        "paper": paper,
                        "is_duplicate": True,
                        "already_has_pdf": False,
                    }
            else:
                # Add new paper
                paper = db.add_paper(paper_data)
                return {"paper": paper, "is_duplicate": False}
