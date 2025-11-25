"""Service for importing PDF files and extracting metadata."""

import json
import logging
from pathlib import Path
from typing import Dict, Optional

from .pdf_parser import PDFParser
from .ai_extractor import AIExtractor
from .db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class ImportService:
    """Service for orchestrating PDF import workflow."""

    def __init__(
        self,
        pdf_parser: PDFParser,
        ai_extractor: Optional[AIExtractor] = None
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
        self,
        file_content: bytes,
        filename: str,
        ai_config: Optional[Dict] = None
    ) -> Dict:
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
        with open(file_path, "wb") as f:
            f.write(file_content)

        # Extract text and metadata from PDF
        extracted = self.pdf_parser.extract_text_and_metadata(str(file_path))

        # Create paper record
        paper_data = {
            "title": extracted.get("title") or filename.replace(".pdf", ""),
            "author": extracted.get("author"),
            "full_text": extracted.get("full_text"),
            "pdf_path": str(file_path)
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
                        ollama_url=ai_config.get("ollamaUrl", "http://localhost:11434")
                    )
                else:
                    extractor = self.ai_extractor

                ai_metadata = extractor.extract_metadata(
                    extracted.get("full_text", "")
                )

                # Merge AI-extracted metadata
                if "study_metadata" in ai_metadata:
                    paper_data["study_metadata"] = ai_metadata["study_metadata"]
                if "learning_science_metadata" in ai_metadata:
                    paper_data["learning_science_metadata"] = (
                        ai_metadata["learning_science_metadata"]
                    )
            except Exception as e:
                # Log but don't fail the import if AI extraction fails
                logger.warning(
                    f"AI extraction failed: {str(e)}, continuing without AI metadata"
                )

        # Save to database
        with DatabaseManager() as db:
            paper = db.add_paper(paper_data)

        return paper


