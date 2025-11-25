"""Conflict detection using Natural Language Inference (NLI) models."""

from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Optional: Only import if transformers is available
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("transformers library not available. Conflict detection will be disabled.")


class ConflictDetector:
    """
    Detects contradictions between study findings using NLI models.

    Uses a pre-trained NLI model (e.g., DeBERTa fine-tuned on MNLI)
    to identify contradictory findings across papers.
    """

    def __init__(self, model_name: str = "cross-encoder/nli-deberta-v3-base"):
        """
        Initialize NLI pipeline.

        Args:
            model_name: Hugging Face model identifier for NLI model
        """
        self.model_name = model_name
        self.nli_pipeline = None

        if TRANSFORMERS_AVAILABLE:
            try:
                self.nli_pipeline = pipeline(
                    "text-classification",
                    model=model_name,
                    device=-1,  # Use CPU (-1), set to 0 for GPU if available
                )
                logger.info(f"Loaded NLI model: {model_name}")
            except Exception as e:
                logger.error(f"Failed to load NLI model: {str(e)}")
                self.nli_pipeline = None
        else:
            logger.warning("transformers not available. Conflict detection disabled.")

    def find_contradictions(
        self,
        findings1: List[str],
        findings2: List[str],
        confidence_threshold: float = 0.8,
    ) -> List[Dict]:
        """
        Compare two lists of findings and identify contradictions.

        Args:
            findings1: List of finding statements from first study
            findings2: List of finding statements from second study
            confidence_threshold: Minimum confidence score for contradiction (0.0 to 1.0)

        Returns:
            List of contradiction dictionaries with:
                - finding1: First finding statement
                - finding2: Second finding statement
                - confidence: Confidence score (0.0 to 1.0)
                - label: NLI label (contradiction/entailment/neutral)
        """
        if self.nli_pipeline is None:
            logger.warning("NLI pipeline not available. Returning empty results.")
            return []

        contradictions = []

        for f1 in findings1:
            for f2 in findings2:
                try:
                    # Format for NLI: premise [SEP] hypothesis
                    result = self.nli_pipeline(f"{f1} [SEP] {f2}")

                    # Handle different return formats
                    if isinstance(result, list) and len(result) > 0:
                        result = result[0]

                    label = result.get("label", "").lower()
                    score = result.get("score", 0.0)

                    # Check for contradiction
                    if "contradict" in label and score >= confidence_threshold:
                        contradictions.append(
                            {
                                "finding1": f1,
                                "finding2": f2,
                                "confidence": float(score),
                                "label": label,
                            }
                        )
                except Exception as e:
                    logger.error(f"Error processing findings: {str(e)}")
                    continue

        return contradictions

    def extract_key_findings(self, paper_text: str, max_findings: int = 5) -> List[str]:
        """
        Extract key findings from paper text (simple keyword-based approach).

        This is a placeholder. In production, use AI extraction or structured data.

        Args:
            paper_text: Full text of the paper
            max_findings: Maximum number of findings to extract

        Returns:
            List of finding statements
        """
        if not paper_text:
            return []

        # Simple keyword-based extraction (placeholder)
        # In production, use AI extraction or structured data from database
        findings = []

        # Look for common finding patterns
        keywords = ["significant", "found that", "results show", "conclusion"]
        sentences = paper_text.split(".")

        for sentence in sentences:
            if any(kw in sentence.lower() for kw in keywords):
                findings.append(sentence.strip())
                if len(findings) >= max_findings:
                    break

        return findings

