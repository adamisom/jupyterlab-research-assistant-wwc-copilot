"""API route handlers for the research assistant extension."""

import json
import logging
from typing import Optional

import numpy as np
import tornado
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join

from .services.conflict_detector import ConflictDetector
from .services.db_manager import DatabaseManager
from .services.export_formatter import ExportFormatter
from .services.import_service import ImportService
from .services.meta_analyzer import MetaAnalyzer
from .services.pdf_parser import PDFParser
from .services.semantic_scholar import SemanticScholarAPI
from .services.visualizer import Visualizer
from .services.wwc_assessor import WWCQualityAssessor

logger = logging.getLogger(__name__)


class BaseAPIHandler(APIHandler):
    """Base handler with common error handling and response methods."""

    def send_success(self, data, status_code=200):
        """Send a successful response."""
        self.set_status(status_code)
        self.finish(json.dumps({"status": "success", "data": data}))

    def send_error(self, status_code=500, message: Optional[str] = None, **kwargs):
        """
        Send an error response.

        Compatible with Tornado's send_error signature which may pass exc_info.
        """
        if message is None:
            # Extract message from exception if available
            if "exc_info" in kwargs:
                _exc_type, exc_value, _ = kwargs["exc_info"]
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

    def _parse_ai_config(self) -> Optional[dict]:
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

    def _get_ai_config(self) -> Optional[dict]:
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
                    # Use first available outcome
                    elif effect_sizes:
                        first_outcome = next(iter(effect_sizes.values()))
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


class ConflictDetectionHandler(BaseAPIHandler):
    """Handler for conflict detection."""

    @tornado.web.authenticated
    def post(self):
        """Detect conflicts between papers."""
        try:
            data = self.get_json_body()
            if not data:
                self.send_error(400, "No data provided")
                return

            paper_ids = data.get("paper_ids", [])
            confidence_threshold = data.get("confidence_threshold", 0.8)

            if len(paper_ids) < 2:
                self.send_error(400, "At least 2 papers required for conflict detection")
                return

            # Fetch papers from database
            with DatabaseManager() as db:
                papers = []
                for paper_id in paper_ids:
                    paper = db.get_paper_by_id(paper_id)
                    if paper:
                        papers.append(paper)

                if len(papers) < 2:
                    self.send_error(400, "Insufficient papers found")
                    return

                # Extract findings and detect conflicts
                detector = ConflictDetector()
                all_contradictions = []

                # Compare each pair of papers
                for i in range(len(papers)):
                    for j in range(i + 1, len(papers)):
                        paper1 = papers[i]
                        paper2 = papers[j]

                        # Extract findings (placeholder - use AI extraction in production)
                        findings1 = detector.extract_key_findings(
                            paper1.get("full_text", "") or paper1.get("abstract", "")
                        )
                        findings2 = detector.extract_key_findings(
                            paper2.get("full_text", "") or paper2.get("abstract", "")
                        )

                        if findings1 and findings2:
                            contradictions = detector.find_contradictions(
                                findings1, findings2, confidence_threshold=confidence_threshold
                            )

                            for contradiction in contradictions:
                                contradiction["paper1_id"] = paper1["id"]
                                contradiction["paper1_title"] = paper1["title"]
                                contradiction["paper2_id"] = paper2["id"]
                                contradiction["paper2_title"] = paper2["title"]
                                all_contradictions.append(contradiction)

                self.send_success(
                    {
                        "contradictions": all_contradictions,
                        "n_papers": len(papers),
                        "n_contradictions": len(all_contradictions),
                    }
                )
        except Exception as e:
            logger.exception("Conflict detection failed")
            self.send_error(500, str(e))


class MetaAnalysisExportHandler(BaseAPIHandler):
    """Handler for exporting meta-analysis as CSV."""

    @tornado.web.authenticated
    def post(self):
        """Export meta-analysis results as CSV."""
        try:
            data = self.get_json_body()
            if not data:
                self.send_error(400, "No data provided")
                return

            paper_ids = data.get("paper_ids", [])
            outcome_name = data.get("outcome_name")

            if len(paper_ids) < 2:
                self.send_error(400, "At least 2 papers required for meta-analysis")
                return

            # Fetch papers and perform meta-analysis
            with DatabaseManager() as db:
                studies = []
                for paper_id in paper_ids:
                    paper = db.get_paper_by_id(paper_id)
                    if not paper:
                        continue

                    study_metadata = paper.get("study_metadata", {})
                    effect_sizes = study_metadata.get("effect_sizes", {})

                    if outcome_name:
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
                    elif effect_sizes:
                        first_outcome = next(iter(effect_sizes.values()))
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

                # Generate CSV
                formatter = ExportFormatter()
                csv_content = formatter.export_meta_analysis_csv(result, result["studies"])

                # Set headers for file download (clear default JSON content type)
                self.clear_header("Content-Type")
                self.set_header("Content-Type", "text/csv")
                self.set_header(
                    "Content-Disposition",
                    f'attachment; filename="meta_analysis_{len(studies)}_studies.csv"',
                )
                self.set_status(200)
                self.finish(csv_content)
        except Exception as e:
            logger.exception("Meta-analysis export failed")
            self.send_error(500, str(e))


class SynthesisExportHandler(BaseAPIHandler):
    """Handler for exporting synthesis report as Markdown."""

    @tornado.web.authenticated
    def post(self):
        """Export synthesis report as Markdown."""
        try:
            data = self.get_json_body()
            if not data:
                self.send_error(400, "No data provided")
                return

            paper_ids = data.get("paper_ids", [])
            include_meta_analysis = data.get("include_meta_analysis", True)
            include_conflicts = data.get("include_conflicts", True)
            include_wwc_assessments = data.get("include_wwc_assessments", False)

            if len(paper_ids) < 2:
                self.send_error(400, "At least 2 papers required for synthesis")
                return

            # Fetch papers
            with DatabaseManager() as db:
                papers = []
                for paper_id in paper_ids:
                    paper = db.get_paper_by_id(paper_id)
                    if paper:
                        papers.append(paper)

                if len(papers) < 2:
                    self.send_error(400, "Insufficient papers found")
                    return

                meta_analysis_result = None
                conflict_result = None

                # Perform meta-analysis if requested
                if include_meta_analysis:
                    try:
                        studies = []
                        for paper in papers:
                            study_metadata = paper.get("study_metadata", {})
                            effect_sizes = study_metadata.get("effect_sizes", {})
                            if effect_sizes:
                                first_outcome = next(iter(effect_sizes.values()))
                                studies.append(
                                    {
                                        "paper_id": paper["id"],
                                        "study_label": paper["title"],
                                        "effect_size": first_outcome.get("d", 0.0),
                                        "std_error": first_outcome.get("se", 0.1),
                                    }
                                )

                        if len(studies) >= 2:
                            analyzer = MetaAnalyzer()
                            meta_analysis_result = analyzer.perform_random_effects_meta_analysis(studies)

                            # Generate forest plot
                            visualizer = Visualizer()
                            forest_plot_base64 = visualizer.create_forest_plot(
                                meta_analysis_result["studies"],
                                meta_analysis_result["pooled_effect"],
                                meta_analysis_result["ci_lower"],
                                meta_analysis_result["ci_upper"],
                                title=f"Meta-Analysis: {len(studies)} Studies",
                            )
                            meta_analysis_result["forest_plot"] = forest_plot_base64
                            meta_analysis_result["heterogeneity_interpretation"] = (
                                analyzer.interpret_heterogeneity(meta_analysis_result["i_squared"])
                            )
                    except Exception as e:
                        logger.warning(f"Meta-analysis failed during export: {e!s}")

                # Perform conflict detection if requested
                if include_conflicts:
                    try:
                        detector = ConflictDetector()
                        all_contradictions = []

                        for i in range(len(papers)):
                            for j in range(i + 1, len(papers)):
                                paper1 = papers[i]
                                paper2 = papers[j]

                                findings1 = detector.extract_key_findings(
                                    paper1.get("full_text", "") or paper1.get("abstract", "")
                                )
                                findings2 = detector.extract_key_findings(
                                    paper2.get("full_text", "") or paper2.get("abstract", "")
                                )

                                if findings1 and findings2:
                                    contradictions = detector.find_contradictions(
                                        findings1, findings2, confidence_threshold=0.8
                                    )

                                    for contradiction in contradictions:
                                        contradiction["paper1_id"] = paper1["id"]
                                        contradiction["paper1_title"] = paper1["title"]
                                        contradiction["paper2_id"] = paper2["id"]
                                        contradiction["paper2_title"] = paper2["title"]
                                        all_contradictions.append(contradiction)

                        conflict_result = {
                            "contradictions": all_contradictions,
                            "n_papers": len(papers),
                            "n_contradictions": len(all_contradictions),
                        }
                    except Exception as e:
                        logger.warning(f"Conflict detection failed during export: {e!s}")

                # Generate Markdown
                formatter = ExportFormatter()
                markdown_content = formatter.export_synthesis_markdown(
                    meta_analysis_result,
                    conflict_result,
                    papers,
                    include_meta_analysis=include_meta_analysis,
                    include_conflicts=include_conflicts,
                    include_wwc_assessments=include_wwc_assessments,
                )

                # Set headers for file download (clear default JSON content type)
                self.clear_header("Content-Type")
                self.set_header("Content-Type", "text/markdown")
                self.set_header(
                    "Content-Disposition",
                    f'attachment; filename="synthesis_report_{len(papers)}_studies.md"',
                )
                self.set_status(200)
                self.finish(markdown_content)
        except Exception as e:
            logger.exception("Synthesis export failed")
            self.send_error(500, str(e))


class SubgroupAnalysisHandler(BaseAPIHandler):
    """Handler for subgroup meta-analysis."""

    @tornado.web.authenticated
    def post(self):
        """Perform subgroup meta-analysis."""
        try:
            data = self.get_json_body()
            if not data:
                self.send_error(400, "No data provided")
                return

            paper_ids = data.get("paper_ids", [])
            subgroup_variable = data.get("subgroup_variable")  # e.g., "age_group"
            outcome_name = data.get("outcome_name")

            if not subgroup_variable:
                self.send_error(400, "subgroup_variable required")
                return

            if len(paper_ids) < 2:
                self.send_error(400, "At least 2 papers required for subgroup analysis")
                return

            # Fetch papers and extract subgroup metadata
            with DatabaseManager() as db:
                studies = []
                for paper_id in paper_ids:
                    paper = db.get_paper_by_id(paper_id)
                    if not paper:
                        continue

                    # Extract effect sizes and subgroup value
                    study_metadata = paper.get("study_metadata", {})
                    effect_sizes = study_metadata.get("effect_sizes", {})
                    learning_metadata = paper.get("learning_science_metadata", {})

                    # Get subgroup value from appropriate metadata field
                    subgroup_value = None
                    if subgroup_variable == "age_group":
                        subgroup_value = learning_metadata.get("age_group")
                    elif subgroup_variable == "intervention_type":
                        subgroup_value = learning_metadata.get("intervention_type")
                    elif subgroup_variable == "learning_domain":
                        subgroup_value = learning_metadata.get("learning_domain")
                    else:
                        # Try to get from study_metadata or top-level
                        subgroup_value = study_metadata.get(subgroup_variable) or paper.get(subgroup_variable)

                    if outcome_name and effect_sizes:
                        outcome_data = effect_sizes.get(outcome_name)
                        if outcome_data and subgroup_value:
                            studies.append({
                                "paper_id": paper["id"],
                                "study_label": paper["title"],
                                "effect_size": outcome_data.get("d", 0.0),
                                "std_error": outcome_data.get("se", 0.1),
                                subgroup_variable: subgroup_value
                            })
                    elif effect_sizes:
                        # Use first available outcome if no outcome_name specified
                        first_outcome = next(iter(effect_sizes.values()))
                        if first_outcome and subgroup_value:
                            studies.append({
                                "paper_id": paper["id"],
                                "study_label": paper["title"],
                                "effect_size": first_outcome.get("d", 0.0),
                                "std_error": first_outcome.get("se", 0.1),
                                subgroup_variable: subgroup_value
                            })

                if len(studies) < 2:
                    self.send_error(400, "Insufficient studies with subgroup data")
                    return

                # Perform subgroup analysis
                analyzer = MetaAnalyzer()
                result = analyzer.perform_subgroup_meta_analysis(studies, subgroup_variable)

                self.send_success(result)
        except Exception as e:
            logger.exception("Subgroup analysis failed")
            self.send_error(500, str(e))


class BiasAssessmentHandler(BaseAPIHandler):
    """Handler for publication bias assessment."""

    @tornado.web.authenticated
    def post(self):
        """Assess publication bias."""
        try:
            data = self.get_json_body()
            if not data:
                self.send_error(400, "No data provided")
                return

            paper_ids = data.get("paper_ids", [])
            outcome_name = data.get("outcome_name")

            if len(paper_ids) < 3:
                self.send_error(400, "At least 3 studies required for bias assessment")
                return

            # Fetch papers and extract effect sizes
            with DatabaseManager() as db:
                studies = []
                for paper_id in paper_ids:
                    paper = db.get_paper_by_id(paper_id)
                    if not paper:
                        continue

                    study_metadata = paper.get("study_metadata", {})
                    effect_sizes = study_metadata.get("effect_sizes", {})

                    if outcome_name:
                        outcome_data = effect_sizes.get(outcome_name)
                        if outcome_data:
                            studies.append({
                                "paper_id": paper["id"],
                                "study_label": paper["title"],
                                "effect_size": outcome_data.get("d", 0.0),
                                "std_error": outcome_data.get("se", 0.1)
                            })
                    elif effect_sizes:
                        # Use first available outcome
                        first_outcome = next(iter(effect_sizes.values()))
                        if first_outcome:
                            studies.append({
                                "paper_id": paper["id"],
                                "study_label": paper["title"],
                                "effect_size": first_outcome.get("d", 0.0),
                                "std_error": first_outcome.get("se", 0.1)
                            })

                if len(studies) < 3:
                    self.send_error(400, "Insufficient studies with effect size data")
                    return

                # Extract arrays
                effect_sizes = np.array([s["effect_size"] for s in studies])
                std_errors = np.array([s["std_error"] for s in studies])
                labels = [s["study_label"] for s in studies]

                # Perform Egger's test
                analyzer = MetaAnalyzer()
                eggers_result = analyzer.perform_eggers_test(effect_sizes, std_errors)

                # Generate funnel plot
                visualizer = Visualizer()
                funnel_plot = visualizer.create_funnel_plot(
                    effect_sizes.tolist(),
                    std_errors.tolist(),
                    labels
                )

                result = {
                    "eggers_test": eggers_result,
                    "funnel_plot": funnel_plot,
                    "n_studies": len(studies)
                }

                self.send_success(result)
        except Exception as e:
            logger.exception("Bias assessment failed")
            self.send_error(500, str(e))


class SensitivityAnalysisHandler(BaseAPIHandler):
    """Handler for sensitivity analysis."""

    @tornado.web.authenticated
    def post(self):
        """Perform sensitivity analysis."""
        try:
            data = self.get_json_body()
            if not data:
                self.send_error(400, "No data provided")
                return

            paper_ids = data.get("paper_ids", [])
            outcome_name = data.get("outcome_name")

            if len(paper_ids) < 3:
                self.send_error(400, "At least 3 studies required for sensitivity analysis")
                return

            # Fetch papers
            with DatabaseManager() as db:
                studies = []
                for paper_id in paper_ids:
                    paper = db.get_paper_by_id(paper_id)
                    if not paper:
                        continue

                    study_metadata = paper.get("study_metadata", {})
                    effect_sizes = study_metadata.get("effect_sizes", {})

                    if outcome_name:
                        outcome_data = effect_sizes.get(outcome_name)
                        if outcome_data:
                            studies.append({
                                "paper_id": paper["id"],
                                "study_label": paper["title"],
                                "effect_size": outcome_data.get("d", 0.0),
                                "std_error": outcome_data.get("se", 0.1)
                            })
                    elif effect_sizes:
                        first_outcome = next(iter(effect_sizes.values()))
                        if first_outcome:
                            studies.append({
                                "paper_id": paper["id"],
                                "study_label": paper["title"],
                                "effect_size": first_outcome.get("d", 0.0),
                                "std_error": first_outcome.get("se", 0.1)
                            })

                if len(studies) < 3:
                    self.send_error(400, "Insufficient studies with effect size data")
                    return

                analyzer = MetaAnalyzer()
                result = analyzer.perform_sensitivity_analysis(studies)

                self.send_success(result)
        except Exception as e:
            logger.exception("Sensitivity analysis failed")
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
        (url_path_join(base_url, route_prefix, "conflict-detection"), ConflictDetectionHandler),
        (url_path_join(base_url, route_prefix, "meta-analysis", "export"), MetaAnalysisExportHandler),
        (url_path_join(base_url, route_prefix, "synthesis", "export"), SynthesisExportHandler),
        (url_path_join(base_url, route_prefix, "subgroup-analysis"), SubgroupAnalysisHandler),
        (url_path_join(base_url, route_prefix, "bias-assessment"), BiasAssessmentHandler),
        (url_path_join(base_url, route_prefix, "sensitivity-analysis"), SensitivityAnalysisHandler),
    ]

    web_app.add_handlers(host_pattern, handlers)
