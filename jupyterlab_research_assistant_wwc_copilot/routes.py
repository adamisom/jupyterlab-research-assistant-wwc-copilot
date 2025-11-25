"""API route handlers for the research assistant extension."""

import json
from pathlib import Path
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado

from .services.semantic_scholar import SemanticScholarAPI
from .services.pdf_parser import PDFParser
from .services.db_manager import DatabaseManager


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

            with DatabaseManager() as db:
                paper = db.add_paper(paper_data)
                self.set_status(201)
                self.finish(json.dumps({"status": "success", "data": paper}))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"status": "error", "message": str(e)}))


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
    ]

    web_app.add_handlers(host_pattern, handlers)
