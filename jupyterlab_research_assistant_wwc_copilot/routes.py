"""API route handlers for the research assistant extension."""

import csv
import io
import json
import logging
from pathlib import Path
from typing import Dict, Optional
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado

from .services.semantic_scholar import SemanticScholarAPI
from .services.pdf_parser import PDFParser
from .services.db_manager import DatabaseManager
from .services.ai_extractor import AIExtractor


class HelloRouteHandler(APIHandler):
    """Test endpoint to verify the extension is loaded."""

    @tornado.web.authenticated
    def get(self):
        """Return a hello message."""
        self.finish(json.dumps({
            "data": (
                "Hello, world!"
                " This is the '/jupyterlab-research-assistant-wwc-copilot/"
                "hello' endpoint. Try visiting me in your browser!"
            ),
        }))


class LibraryHandler(APIHandler):
    """Handler for library CRUD operations."""

    @tornado.web.authenticated
    def get(self):
        """Get all papers in the library."""
        try:
            with DatabaseManager() as db:
                papers = db.get_all_papers()
                self.finish(json.dumps({"status": "success", "data": papers}))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"status": "error", "message": str(e)}))

    @tornado.web.authenticated
    def post(self):
        """Add a new paper to the library."""
        try:
            data = self.get_json_body()
            if data is None or (isinstance(data, dict) and not data):
                self.set_status(400)
                self.finish(json.dumps({
                    "status": "error",
                    "message": "No data provided"
                }))
                return

            with DatabaseManager() as db:
                paper = db.add_paper(data)
                self.set_status(201)
                self.finish(json.dumps({"status": "success", "data": paper}))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"status": "error", "message": str(e)}))


class SearchHandler(APIHandler):
    """Handler for searching the library."""

    @tornado.web.authenticated
    def get(self):
        """Search papers in the library."""
        try:
            query = self.get_argument("q", "")
            if not query:
                self.set_status(400)
                self.finish(json.dumps({
                    "status": "error",
                    "message": "Query parameter 'q' required"
                }))
                return

            with DatabaseManager() as db:
                papers = db.search_papers(query)
                self.finish(json.dumps({"status": "success", "data": papers}))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"status": "error", "message": str(e)}))


class DiscoveryHandler(APIHandler):
    """Handler for Semantic Scholar discovery."""

    @tornado.web.authenticated
    def get(self):
        """Search Semantic Scholar for papers."""
        try:
            query = self.get_argument("q", "")
            year = self.get_argument("year", None)
            limit = int(self.get_argument("limit", "20"))
            offset = int(self.get_argument("offset", "0"))

            if not query:
                self.set_status(400)
                self.finish(json.dumps({
                    "status": "error",
                    "message": "Query parameter 'q' required"
                }))
                return

            api = SemanticScholarAPI()
            results = api.search_papers(
                query, year=year, limit=limit, offset=offset
            )
            self.finish(json.dumps({"status": "success", "data": results}))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"status": "error", "message": str(e)}))


class ImportHandler(APIHandler):
    """Handler for importing PDFs."""

    @tornado.web.authenticated
    def post(self):
        """Import a PDF file and extract metadata."""
        try:
            # Get uploaded file
            if "file" not in self.request.files:
                self.set_status(400)
                self.finish(json.dumps({
                    "status": "error",
                    "message": "No file provided"
                }))
                return

            file_info = self.request.files["file"][0]
            file_content = file_info["body"]
            filename = file_info["filename"]

            # Save file to temporary location
            upload_dir = Path.home() / ".jupyter" / "research_assistant" / "uploads"
            upload_dir.mkdir(parents=True, exist_ok=True)

            file_path = upload_dir / filename
            with open(file_path, "wb") as f:
                f.write(file_content)

            # Extract text and metadata
            parser = PDFParser()
            extracted = parser.extract_text_and_metadata(str(file_path))

            # Create paper record
            paper_data = {
                "title": extracted.get("title") or filename.replace(".pdf", ""),
                "author": extracted.get("author"),
                "full_text": extracted.get("full_text"),
                "pdf_path": str(file_path)
            }

            # AI extraction (if enabled)
            ai_config = self._get_ai_config()
            if ai_config and ai_config.get("enabled"):
                try:
                    extractor = AIExtractor(
                        provider=ai_config.get("provider", "ollama"),
                        api_key=ai_config.get("apiKey"),
                        model=ai_config.get("model", "llama3"),
                        ollama_url=ai_config.get("ollamaUrl", "http://localhost:11434")
                    )
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
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"AI extraction failed: {str(e)}, continuing without AI metadata")

            with DatabaseManager() as db:
                paper = db.add_paper(paper_data)
                self.set_status(201)
                self.finish(json.dumps({"status": "success", "data": paper}))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"status": "error", "message": str(e)}))


    def _get_ai_config(self) -> Optional[Dict]:
        """Get AI extraction configuration from settings."""
        # Try to get settings from JupyterLab settings registry
        # This is a simplified version - in production, you'd read from settings registry
        # For now, return None (disabled by default)
        # TODO: Implement proper settings reading from JupyterLab settings registry
        return None


class ExportHandler(APIHandler):
    """Handler for exporting library."""

    @tornado.web.authenticated
    def get(self):
        """Export library in specified format."""
        try:
            format_type = self.get_argument("format", "json")  # json, csv, bibtex

            with DatabaseManager() as db:
                papers = db.get_all_papers()

            if format_type == "json":
                self.set_header("Content-Type", "application/json")
                self.set_header(
                    "Content-Disposition", "attachment; filename=library.json"
                )
                self.finish(json.dumps(papers, indent=2))

            elif format_type == "csv":
                output = io.StringIO()
                writer = csv.DictWriter(
                    output,
                    fieldnames=[
                        "id",
                        "title",
                        "authors",
                        "year",
                        "doi",
                        "citation_count",
                        "abstract"
                    ]
                )
                writer.writeheader()
                for paper in papers:
                    row = {
                        "id": paper.get("id", ""),
                        "title": paper.get("title", ""),
                        "authors": ", ".join(paper.get("authors", [])),
                        "year": paper.get("year", ""),
                        "doi": paper.get("doi", ""),
                        "citation_count": paper.get("citation_count", ""),
                        "abstract": (paper.get("abstract", "") or "")[:500]  # Truncate
                    }
                    writer.writerow(row)

                self.set_header("Content-Type", "text/csv")
                self.set_header(
                    "Content-Disposition", "attachment; filename=library.csv"
                )
                self.finish(output.getvalue())

            elif format_type == "bibtex":
                bibtex = self._generate_bibtex(papers)
                self.set_header("Content-Type", "text/plain")
                self.set_header(
                    "Content-Disposition", "attachment; filename=library.bib"
                )
                self.finish(bibtex)

            else:
                self.set_status(400)
                self.finish(json.dumps({
                    "status": "error",
                    "message": f"Unknown format: {format_type}"
                }))

        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"status": "error", "message": str(e)}))

    def _generate_bibtex(self, papers: list) -> str:
        """Generate BibTeX entries from papers."""
        entries = []
        for paper in papers:
            # Generate citation key from first author and year
            authors = paper.get("authors", [])
            year = paper.get("year", "unknown")
            first_author = (
                authors[0].split()[-1].lower() if authors else "unknown"
            )
            citation_key = f"{first_author}{year}"

            # Determine entry type (default to @article)
            entry_type = "@article"

            entry = f"{entry_type}{{{citation_key},\n"
            entry += f"  title = {{{paper.get('title', '')}}},\n"

            if authors:
                entry += f"  author = {{{' and '.join(authors)}}},\n"

            if year:
                entry += f"  year = {{{year}}},\n"

            if paper.get("doi"):
                entry += f"  doi = {{{paper.get('doi')}}},\n"

            if paper.get("abstract"):
                # Escape special characters for BibTeX
                abstract = (
                    paper.get("abstract", "")
                    .replace("{", "\\{")
                    .replace("}", "\\}")
                )
                entry += f"  abstract = {{{abstract[:200]}...}},\n"

            entry += "}\n"
            entries.append(entry)

        return "\n".join(entries)


def setup_route_handlers(web_app):
    """Register all API route handlers."""
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]
    route_prefix = "jupyterlab-research-assistant-wwc-copilot"

    handlers = [
        (url_path_join(base_url, route_prefix, "hello"), HelloRouteHandler),
        (url_path_join(base_url, route_prefix, "library"), LibraryHandler),
        (url_path_join(base_url, route_prefix, "search"), SearchHandler),
        (url_path_join(base_url, route_prefix, "discovery"), DiscoveryHandler),
        (url_path_join(base_url, route_prefix, "import"), ImportHandler),
        (url_path_join(base_url, route_prefix, "export"), ExportHandler),
    ]

    web_app.add_handlers(host_pattern, handlers)
