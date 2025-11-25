"""API route handlers for the research assistant extension."""

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
from .services.export_formatter import ExportFormatter
from .services.import_service import ImportService
from .services.wwc_assessor import WWCQualityAssessor
from .services.meta_analyzer import MetaAnalyzer
from .services.visualizer import Visualizer

logger = logging.getLogger(__name__)


class BaseAPIHandler(APIHandler):
    """Base handler with common error handling and response methods."""

    def send_success(self, data, status_code=200):
        """Send a successful response."""
        self.set_status(status_code)
        self.finish(json.dumps({"status": "success", "data": data}))

    def send_error(self, status_code=500, message: str = None, **kwargs):
        """
        Send an error response.
        
        Compatible with Tornado's send_error signature which may pass exc_info.
        """
        if message is None:
            # Extract message from exception if available
            if "exc_info" in kwargs:
                exc_type, exc_value, _ = kwargs["exc_info"]
                message = str(exc_value)
            else:
                message = "An error occurred"
        
        self.set_status(status_code)
        self.finish(json.dumps({"status": "error", "message": message}))
    
    def send_error_legacy(self, message: str, status_code=500):
        """
        Legacy send_error method for backward compatibility.
        Use send_error(status_code, message) for Tornado compatibility.
        """
        self.send_error(status_code, message)

    def handle_request(self, handler_func):
        """Execute handler function with error handling."""
        try:
            return handler_func()
        except Exception as e:
            logger.exception("Request failed")
            self.send_error(str(e))


class HelloRouteHandler(BaseAPIHandler):
    """Test endpoint to verify the extension is loaded."""

    @tornado.web.authenticated
    def get(self):
        """Return a hello message."""
        self.send_success(
            "Hello, world! This is the '/jupyterlab-research-assistant-wwc-copilot/hello' endpoint. Try visiting me in your browser!"
        )


class LibraryHandler(BaseAPIHandler):
    """Handler for library CRUD operations."""

    @tornado.web.authenticated
    def get(self):
        """Get all papers in the library."""
        with DatabaseManager() as db:
            papers = db.get_all_papers()
            self.send_success(papers)

    @tornado.web.authenticated
    def post(self):
        """Add a new paper to the library."""
        data = self.get_json_body()
        if data is None or (isinstance(data, dict) and not data):
            self.send_error(400, "No data provided")
            return

        with DatabaseManager() as db:
            paper = db.add_paper(data)
            self.send_success(paper, 201)


class SearchHandler(BaseAPIHandler):
    """Handler for searching the library."""

    @tornado.web.authenticated
    def get(self):
        """Search papers in the library."""
        query = self.get_argument("q", "")
        if not query:
            self.send_error(400, "Query parameter 'q' required")
            return

        with DatabaseManager() as db:
            papers = db.search_papers(query)
            self.send_success(papers)


class DiscoveryHandler(BaseAPIHandler):
    """Handler for Semantic Scholar discovery."""

    @tornado.web.authenticated
    def get(self):
        """Search Semantic Scholar for papers."""
        query = self.get_argument("q", "")
        year = self.get_argument("year", None)
        limit = int(self.get_argument("limit", "20"))
        offset = int(self.get_argument("offset", "0"))

        if not query:
            self.send_error(400, "Query parameter 'q' required")
            return

        api = SemanticScholarAPI()
        results = api.search_papers(
            query, year=year, limit=limit, offset=offset
        )
        self.send_success(results)


class ImportHandler(BaseAPIHandler):
    """Handler for importing PDFs."""

    @tornado.web.authenticated
    def post(self):
        """Import a PDF file and extract metadata."""
        # Get uploaded file
        if "file" not in self.request.files:
            self.send_error(400, "No file provided")
            return

        file_info = self.request.files["file"][0]
        file_content = file_info["body"]
        filename = file_info["filename"]

        # Parse AI config from form data
        ai_config = self._parse_ai_config()
        if not ai_config:
            ai_config = self._get_ai_config()

        # Import using service
        pdf_parser = PDFParser()
        import_service = ImportService(
            pdf_parser=pdf_parser,
            ai_extractor=None  # Will be created by service if needed
        )

        paper = import_service.import_pdf(
            file_content=file_content,
            filename=filename,
            ai_config=ai_config
        )

        self.send_success(paper, 201)

    def _parse_ai_config(self) -> Optional[Dict]:
        """Parse AI config from form data."""
        if "aiConfig" not in self.request.files:
            return None

        try:
            ai_config_data = self.request.files["aiConfig"][0]["body"]
            if isinstance(ai_config_data, bytes):
                ai_config_str = ai_config_data.decode("utf-8")
            else:
                ai_config_str = str(ai_config_data)
            return json.loads(ai_config_str)
        except (json.JSONDecodeError, KeyError, IndexError, TypeError):
            return None

    def _get_ai_config(self) -> Optional[Dict]:
        """Get AI extraction configuration from settings."""
        # Try to get settings from JupyterLab settings registry
        # This is a simplified version - in production, you'd read from settings registry
        # For now, return None (disabled by default)
        # TODO: Implement proper settings reading from JupyterLab settings registry
        return None


class ExportHandler(BaseAPIHandler):
    """Handler for exporting library."""

    @tornado.web.authenticated
    def get(self):
        """Export library in specified format."""
        format_type = self.get_argument("format", "json")  # json, csv, bibtex

        with DatabaseManager() as db:
            papers = db.get_all_papers()

        formatter = ExportFormatter()

        if format_type == "json":
            content = formatter.to_json(papers)
            self.set_header("Content-Type", "application/json")
            self.set_header(
                "Content-Disposition", "attachment; filename=library.json"
            )
            self.finish(content)

        elif format_type == "csv":
            content = formatter.to_csv(papers)
            self.set_header("Content-Type", "text/csv")
            self.set_header(
                "Content-Disposition", "attachment; filename=library.csv"
            )
            self.finish(content)

        elif format_type == "bibtex":
            content = formatter.to_bibtex(papers)
            self.set_header("Content-Type", "text/plain")
            self.set_header(
                "Content-Disposition", "attachment; filename=library.bib"
            )
            self.finish(content)

        else:
            self.send_error(400, f"Unknown format: {format_type}")


class WWCAssessmentHandler(BaseAPIHandler):
    """Handler for WWC quality assessment."""

    @tornado.web.authenticated
    def post(self):
        """Run WWC assessment for a paper."""
        try:
            data = self.get_json_body()
            if not data:
                self.send_error(400, "No data provided")
                return

            paper_id = data.get("paper_id")
            if not paper_id:
                self.send_error(400, "paper_id required")
                return

            # Fetch paper from database
            with DatabaseManager() as db:
                paper = db.get_paper_by_id(paper_id)
                if not paper:
                    self.send_error(404, "Paper not found")
                    return

                # Prepare extracted data from paper
                study_metadata = paper.get("study_metadata", {})
                extracted_data = {
                    "paper_id": paper["id"],
                    "paper_title": paper["title"],
                    "methodology": study_metadata.get("methodology"),
                    "baseline_n": study_metadata.get("sample_size_baseline"),
                    "endline_n": study_metadata.get("sample_size_endline"),
                    "randomization_documented": None,  # Will be set from user judgment or extraction
                }

                # Extract attrition data if available
                # Note: This assumes attrition rates are stored in study_metadata
                # You may need to extract from full_text using AI if not available
                treatment_attrition = study_metadata.get("treatment_attrition")
                control_attrition = study_metadata.get("control_attrition")
                if treatment_attrition is not None:
                    extracted_data["treatment_attrition"] = treatment_attrition
                if control_attrition is not None:
                    extracted_data["control_attrition"] = control_attrition

                # Extract baseline equivalence data if available
                baseline_means = study_metadata.get("baseline_means")
                baseline_sds = study_metadata.get("baseline_sds")
                if baseline_means:
                    extracted_data["baseline_means"] = baseline_means
                if baseline_sds:
                    extracted_data["baseline_sds"] = baseline_sds

                # User judgments
                user_judgments = data.get("judgments", {})

                # Run assessment
                assessor = WWCQualityAssessor()
                assessment = assessor.assess(extracted_data, user_judgments)

                # Convert to dict for JSON response
                result = assessor.assessment_to_dict(assessment)

                self.send_success(result)
        except Exception as e:
            logger.exception("WWC assessment failed")
            self.send_error(500, str(e))


class MetaAnalysisHandler(BaseAPIHandler):
    """Handler for meta-analysis."""

    @tornado.web.authenticated
    def post(self):
        """Perform meta-analysis on selected papers."""
        try:
            data = self.get_json_body()
            if not data:
                self.send_error(400, "No data provided")
                return

            paper_ids = data.get("paper_ids", [])
            outcome_name = data.get("outcome_name")  # Optional: specific outcome to analyze

            if len(paper_ids) < 2:
                self.send_error(400, "At least 2 papers required for meta-analysis")
                return

            # Fetch papers from database
            with DatabaseManager() as db:
                studies = []
                for paper_id in paper_ids:
                    paper = db.get_paper_by_id(paper_id)
                    if not paper:
                        continue

                    # Extract effect sizes
                    study_metadata = paper.get("study_metadata", {})
                    effect_sizes = study_metadata.get("effect_sizes", {})

                    if outcome_name:
                        # Use specific outcome
                        outcome_data = effect_sizes.get(outcome_name)
                        if outcome_data:
                            studies.append(
                                {
                                    "paper_id": paper["id"],
                                    "study_label": paper["title"],
                                    "effect_size": outcome_data.get("d", 0.0),
                                    "std_error": outcome_data.get("se", 0.1),
                                }
                            )
                    else:
                        # Use first available outcome
                        if effect_sizes:
                            first_outcome = list(effect_sizes.values())[0]
                            studies.append(
                                {
                                    "paper_id": paper["id"],
                                    "study_label": paper["title"],
                                    "effect_size": first_outcome.get("d", 0.0),
                                    "std_error": first_outcome.get("se", 0.1),
                                }
                            )

                if len(studies) < 2:
                    self.send_error(400, "Insufficient studies with effect size data")
                    return

                # Perform meta-analysis
                analyzer = MetaAnalyzer()
                result = analyzer.perform_random_effects_meta_analysis(studies)

                # Generate forest plot
                visualizer = Visualizer()
                forest_plot_base64 = visualizer.create_forest_plot(
                    result["studies"],
                    result["pooled_effect"],
                    result["ci_lower"],
                    result["ci_upper"],
                    title=f"Meta-Analysis: {len(studies)} Studies",
                )

                result["forest_plot"] = forest_plot_base64
                result["heterogeneity_interpretation"] = analyzer.interpret_heterogeneity(
                    result["i_squared"]
                )

                self.send_success(result)
        except Exception as e:
            logger.exception("Meta-analysis failed")
            self.send_error(500, str(e))


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
        (url_path_join(base_url, route_prefix, "wwc-assessment"), WWCAssessmentHandler),
        (url_path_join(base_url, route_prefix, "meta-analysis"), MetaAnalysisHandler),
    ]

    web_app.add_handlers(host_pattern, handlers)
